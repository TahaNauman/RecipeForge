from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    cuisine: Mapped[str | None] = mapped_column(String(50))
    difficulty: Mapped[str | None] = mapped_column(String(20))
    prep_time: Mapped[int | None]
    cook_time: Mapped[int | None]
    servings: Mapped[int | None]
    forked_from_recipe_id: Mapped[int | None] = mapped_column(
        ForeignKey("recipes.id"), index=True
    )
    forked_from_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("recipe_versions.id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    author: Mapped["User"] = relationship(lazy="joined")
    versions: Mapped[list["RecipeVersion"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
        foreign_keys="RecipeVersion.recipe_id",
    )


class RecipeVersion(Base):
    __tablename__ = "recipe_versions"
    __table_args__ = (UniqueConstraint("recipe_id", "version_number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), index=True)
    version_number: Mapped[str] = mapped_column(String(20))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    parent_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("recipe_versions.id")
    )
    change_description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    recipe: Mapped["Recipe"] = relationship(
        back_populates="versions", foreign_keys="RecipeVersion.recipe_id"
    )
    author: Mapped["User"] = relationship(lazy="joined")
    ingredients: Mapped[list["RecipeVersionIngredient"]] = relationship(
        cascade="all, delete-orphan", order_by="RecipeVersionIngredient.sort_order"
    )
    instructions: Mapped[list["RecipeVersionInstruction"]] = relationship(
        cascade="all, delete-orphan", order_by="RecipeVersionInstruction.step_number"
    )


class RecipeVersionIngredient(Base):
    __tablename__ = "recipe_version_ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    version_id: Mapped[int] = mapped_column(ForeignKey("recipe_versions.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    quantity: Mapped[float | None] = mapped_column(Numeric(10, 2))
    unit: Mapped[str | None] = mapped_column(String(30))
    sort_order: Mapped[int] = mapped_column(default=0)


class RecipeVersionInstruction(Base):
    __tablename__ = "recipe_version_instructions"

    id: Mapped[int] = mapped_column(primary_key=True)
    version_id: Mapped[int] = mapped_column(ForeignKey("recipe_versions.id"), index=True)
    step_number: Mapped[int]
    text: Mapped[str] = mapped_column(Text)