from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class IngredientInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    quantity: float | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, max_length=30)


class InstructionInput(BaseModel):
    text: str = Field(min_length=1)


class RecipeBase(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str | None = None
    cuisine: str | None = Field(default=None, max_length=50)
    difficulty: str | None = Field(default=None, max_length=20)
    prep_time: int | None = Field(default=None, ge=0)
    cook_time: int | None = Field(default=None, ge=0)
    servings: int | None = Field(default=None, ge=1)


class RecipeCreate(RecipeBase):
    ingredients: list[IngredientInput] = Field(min_length=1)
    instructions: list[InstructionInput] = Field(min_length=1)
    change_description: str | None = Field(default=None, max_length=200)


class RecipeUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = None
    cuisine: str | None = Field(default=None, max_length=50)
    difficulty: str | None = Field(default=None, max_length=20)
    prep_time: int | None = Field(default=None, ge=0)
    cook_time: int | None = Field(default=None, ge=0)
    servings: int | None = Field(default=None, ge=1)
    ingredients: list[IngredientInput] | None = None
    instructions: list[InstructionInput] | None = None
    change_description: str | None = Field(default=None, max_length=200)


class IngredientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    quantity: float | None
    unit: str | None


class InstructionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    step_number: int
    text: str


class RecipeVersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    version_number: str
    parent_version_id: int | None
    author_username: str
    change_description: str | None
    created_at: datetime
    ingredients: list[IngredientOut]
    instructions: list[InstructionOut]


class RecipeVersionHeader(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    version_number: str
    author_username: str
    change_description: str | None
    created_at: datetime
    ingredient_count: int


class RecipeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    cuisine: str | None
    difficulty: str | None
    prep_time: int | None
    cook_time: int | None
    servings: int | None
    created_at: datetime
    updated_at: datetime
    author_username: str
    version: RecipeVersionOut


class RecipeListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    cuisine: str | None
    difficulty: str | None
    prep_time: int | None
    cook_time: int | None
    servings: int | None
    created_at: datetime
    author_username: str
    version_number: str
    ingredient_count: int