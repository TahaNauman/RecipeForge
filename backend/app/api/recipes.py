from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models import Recipe, RecipeVersion, RecipeVersionIngredient, \
    RecipeVersionInstruction, User
from app.schemas.recipe import (
    IngredientOut,
    InstructionOut,
    RecipeCreate,
    RecipeListItem,
    RecipeOut,
    RecipeUpdate,
    RecipeVersionOut,
)

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


def _recipe_query(db: Session):
    return db.query(Recipe).options(
        selectinload(Recipe.versions).selectinload(RecipeVersion.ingredients),
        selectinload(Recipe.versions).selectinload(RecipeVersion.instructions),
    )


def _latest_version(recipe: Recipe) -> RecipeVersion:
    return max(recipe.versions, key=lambda v: v.version_number)


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
        version=RecipeVersionOut(
            version_number=version.version_number,
            created_at=version.created_at,
            ingredients=[IngredientOut.model_validate(i) for i in version.ingredients],
            instructions=[InstructionOut.model_validate(i) for i in version.instructions],
        ),
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
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field in ("ingredients", "instructions"):
            continue
        setattr(recipe, field, value)
    if payload.ingredients is not None or payload.instructions is not None:
        version = _latest_version(recipe)
        version.ingredients.clear()
        version.instructions.clear()
        if payload.ingredients is not None:
            for i, ing in enumerate(payload.ingredients):
                version.ingredients.append(
                    RecipeVersionIngredient(name=ing.name, quantity=ing.quantity, unit=ing.unit, sort_order=i)
                )
        if payload.instructions is not None:
            for i, ins in enumerate(payload.instructions):
                version.instructions.append(RecipeVersionInstruction(step_number=i + 1, text=ins.text))
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