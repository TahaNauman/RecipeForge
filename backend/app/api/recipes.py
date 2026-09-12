from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models import Recipe, RecipeVersion, RecipeVersionIngredient, \
    RecipeVersionInstruction, User
from app.schemas.recipe import (
    IngredientInput,
    IngredientOut,
    InstructionInput,
    InstructionOut,
    RecipeCreate,
    RecipeListItem,
    RecipeOut,
    RecipeUpdate,
    RecipeVersionHeader,
    RecipeVersionOut,
)

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


def _recipe_query(db: Session):
    return db.query(Recipe).options(
        selectinload(Recipe.versions).selectinload(RecipeVersion.ingredients),
        selectinload(Recipe.versions).selectinload(RecipeVersion.instructions),
    )


def _latest_version(recipe: Recipe) -> RecipeVersion:
    return max(recipe.versions, key=_version_key)


def _version_key(version: RecipeVersion) -> tuple[int, int]:
    parts = version.version_number.split(".")
    return (int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)


def _next_version_number(version: RecipeVersion) -> str:
    major, minor = _version_key(version)
    return f"{major}.{minor + 1}"


def _q(value) -> float | None:
    return None if value is None else float(value)


def _build_snapshot(version: RecipeVersion, ingredients, instructions) -> None:
    for i, ing in enumerate(ingredients):
        version.ingredients.append(
            RecipeVersionIngredient(name=ing.name, quantity=ing.quantity, unit=ing.unit, sort_order=i)
        )
    for i, ins in enumerate(instructions):
        version.instructions.append(RecipeVersionInstruction(step_number=i + 1, text=ins.text))


def _get_recipe_or_404(db: Session, recipe_id: int) -> Recipe:
    recipe = _recipe_query(db).filter(Recipe.id == recipe_id).first()
    if recipe is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    return recipe


def _version_out(version: RecipeVersion) -> RecipeVersionOut:
    return RecipeVersionOut(
        id=version.id,
        version_number=version.version_number,
        parent_version_id=version.parent_version_id,
        author_username=version.author.username,
        change_description=version.change_description,
        created_at=version.created_at,
        ingredients=[IngredientOut.model_validate(i) for i in version.ingredients],
        instructions=[InstructionOut.model_validate(i) for i in version.instructions],
    )


def _version_header(version: RecipeVersion) -> RecipeVersionHeader:
    return RecipeVersionHeader(
        id=version.id,
        version_number=version.version_number,
        author_username=version.author.username,
        change_description=version.change_description,
        created_at=version.created_at,
        ingredient_count=len(version.ingredients),
    )


def _recipe_out(recipe: Recipe) -> RecipeOut:
    version = _latest_version(recipe)
    return RecipeOut(
        id=recipe.id,
        title=recipe.title,
        description=recipe.description,
        cuisine=recipe.cuisine,
        difficulty=recipe.difficulty,
        prep_time=recipe.prep_time,
        cook_time=recipe.cook_time,
        servings=recipe.servings,
        created_at=recipe.created_at,
        updated_at=recipe.updated_at,
        author_username=recipe.author.username,
        version=_version_out(version),
    )


def _list_item(recipe: Recipe) -> RecipeListItem:
    version = _latest_version(recipe)
    return RecipeListItem(
        id=recipe.id,
        title=recipe.title,
        cuisine=recipe.cuisine,
        difficulty=recipe.difficulty,
        prep_time=recipe.prep_time,
        cook_time=recipe.cook_time,
        servings=recipe.servings,
        created_at=recipe.created_at,
        author_username=recipe.author.username,
        version_number=version.version_number,
        ingredient_count=len(version.ingredients),
    )


@router.get("", response_model=list[RecipeListItem])
def list_recipes(db: Session = Depends(get_db)):
    return [_list_item(r) for r in _recipe_query(db).order_by(Recipe.created_at.desc())]


@router.post("", response_model=RecipeOut, status_code=status.HTTP_201_CREATED)
def create_recipe(payload: RecipeCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    recipe = Recipe(
        author_id=user.id,
        title=payload.title,
        description=payload.description,
        cuisine=payload.cuisine,
        difficulty=payload.difficulty,
        prep_time=payload.prep_time,
        cook_time=payload.cook_time,
        servings=payload.servings,
    )
    db.add(recipe)
    db.flush()
    version = RecipeVersion(recipe_id=recipe.id, version_number="1.0", author_id=user.id)
    db.add(version)
    db.flush()
    _build_snapshot(version, payload.ingredients, payload.instructions)
    db.commit()
    db.refresh(recipe)
    return _recipe_out(recipe)


@router.get("/{recipe_id}", response_model=RecipeOut)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    return _recipe_out(_get_recipe_or_404(db, recipe_id))


@router.get("/{recipe_id}/versions", response_model=list[RecipeVersionHeader])
def list_versions(recipe_id: int, db: Session = Depends(get_db)):
    recipe = _get_recipe_or_404(db, recipe_id)
    versions = sorted(recipe.versions, key=_version_key, reverse=True)
    return [_version_header(v) for v in versions]


@router.get("/{recipe_id}/versions/{version_id}", response_model=RecipeVersionOut)
def get_version(recipe_id: int, version_id: int, db: Session = Depends(get_db)):
    recipe = _get_recipe_or_404(db, recipe_id)
    version = next((v for v in recipe.versions if v.id == version_id), None)
    if version is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Version not found")
    return _version_out(version)


def _current_metadata(recipe: Recipe) -> dict:
    return {
        "title": recipe.title,
        "description": recipe.description,
        "cuisine": recipe.cuisine,
        "difficulty": recipe.difficulty,
        "prep_time": recipe.prep_time,
        "cook_time": recipe.cook_time,
        "servings": recipe.servings,
    }


def _effective_metadata(recipe: Recipe, payload: RecipeUpdate) -> dict:
    data = payload.model_dump(exclude_unset=True)
    current = _current_metadata(recipe)
    return {field: data.get(field, current[field]) for field in current}


def _merged_snapshot(prev: RecipeVersion, payload: RecipeUpdate):
    ings = payload.ingredients if payload.ingredients is not None else [
        IngredientInput(name=i.name, quantity=_q(i.quantity), unit=i.unit) for i in prev.ingredients
    ]
    steps = payload.instructions if payload.instructions is not None else [
        InstructionInput(text=i.text) for i in prev.instructions
    ]
    return ings, steps


def _snapshots_match(prev: RecipeVersion, ings, steps) -> bool:
    return (
        [i.name for i in prev.ingredients] == [i.name for i in ings]
        and [_q(i.quantity) for i in prev.ingredients] == [_q(i.quantity) for i in ings]
        and [i.unit for i in prev.ingredients] == [i.unit for i in ings]
        and [i.text for i in prev.instructions] == [i.text for i in steps]
    )


@router.put("/{recipe_id}", response_model=RecipeOut)
def update_recipe(
    recipe_id: int,
    payload: RecipeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    recipe = _get_recipe_or_404(db, recipe_id)
    if recipe.author_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Only the author can edit this recipe")
    prev = _latest_version(recipe)
    ings, steps = _merged_snapshot(prev, payload)
    meta = _effective_metadata(recipe, payload)
    if _snapshots_match(prev, ings, steps) and meta == _current_metadata(recipe):
        return _recipe_out(recipe)
    for field, value in meta.items():
        setattr(recipe, field, value)
    version = RecipeVersion(
        recipe_id=recipe.id,
        version_number=_next_version_number(prev),
        parent_version_id=prev.id,
        author_id=user.id,
        change_description=payload.change_description,
    )
    db.add(version)
    db.flush()
    _build_snapshot(version, ings, steps)
    db.commit()
    db.refresh(recipe)
    return _recipe_out(recipe)


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    recipe = _get_recipe_or_404(db, recipe_id)
    if recipe.author_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Only the author can delete this recipe")
    db.delete(recipe)
    db.commit()