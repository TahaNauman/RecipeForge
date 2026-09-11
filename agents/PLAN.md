# RecipeForge — Development Plan

## Overview

**RecipeForge** is a full-stack portfolio project: GitHub for recipes. Recipes have versions, forks, diffs, lineage, and contributors. The identity is version-controlled cooking, not a CRUD recipe app.

## Tech Stack

| Layer | Choice |
|-------|--------|
| Frontend | Next.js (App Router), TypeScript, Tailwind CSS, Recharts, React Flow |
| Backend | Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2.0 (sync), Alembic |
| Database | PostgreSQL 16 |
| Infra | Docker Compose (Postgres only — backend/frontend run on host for fast dev) |
| Auth | JWT single access token (7-day), bcrypt password hashing |

> **Note (Phase 1):** Deviated from the original plan — SQLAlchemy is **sync**
> with `psycopg` (simpler Alembic + sessions, no perf concern via FastAPI's
> threadpool), and Compose runs **Postgres only** (quality bar only requires
> Postgres in Docker; Next/FastAPI hot-reload is more reliable on the host).
>
> **Note (Phase 2):** Deviated on token strategy — single 7-day JWT access
> token stored in `localStorage` instead of access+refresh. Stateless logout
> (no token blacklist yet). Backend tests run against a separate
> `recipeforge_test` database.

## Monorepo Layout

```
recipeforge/
├── frontend/          # Next.js app
│   ├── app/           # App Router pages
│   ├── components/    # Shared React components
│   ├── lib/           # API client, utilities
│   └── types/         # TypeScript types
├── backend/           # FastAPI app
│   ├── app/
│   │   ├── api/       # Route handlers (grouped by resource)
│   │   ├── models/    # SQLAlchemy ORM models
│   │   ├── schemas/   # Pydantic request/response schemas
│   │   ├── services/  # Business logic (diff, similarity, etc.)
│   │   └── db/        # Engine, session, base
│   ├── alembic/       # Migrations
│   └── tests/         # pytest tests
├── docker-compose.yml
├── README.md
└── agents/            # Planning docs, agent configs
```

## Database Schema (key tables)

```
users
  id                SERIAL PRIMARY KEY
  username          VARCHAR(50) UNIQUE NOT NULL
  email             VARCHAR(255) UNIQUE NOT NULL
  password_hash     VARCHAR(255) NOT NULL
  display_name      VARCHAR(100)
  bio               TEXT
  created_at        TIMESTAMPTZ DEFAULT NOW()

recipes
  id                SERIAL PRIMARY KEY
  author_id         INT REFERENCES users(id)
  title             VARCHAR(200) NOT NULL
  description       TEXT
  cuisine           VARCHAR(50)
  difficulty        VARCHAR(20)
  prep_time         INT  -- minutes
  cook_time         INT  -- minutes
  servings          INT
  forked_from_recipe_id   INT REFERENCES recipes(id) NULL
  forked_from_version_id  INT REFERENCES recipe_versions(id) NULL
  created_at        TIMESTAMPTZ DEFAULT NOW()
  updated_at        TIMESTAMPTZ DEFAULT NOW()

recipe_versions
  id                SERIAL PRIMARY KEY
  recipe_id         INT REFERENCES recipes(id) NOT NULL
  version_number    VARCHAR(20) NOT NULL  -- "1.0", "1.1"
  author_id         INT REFERENCES users(id) NOT NULL
  parent_version_id INT REFERENCES recipe_versions(id) NULL
  change_description TEXT
  created_at        TIMESTAMPTZ DEFAULT NOW()
  UNIQUE(recipe_id, version_number)

recipe_version_ingredients
  id                SERIAL PRIMARY KEY
  version_id        INT REFERENCES recipe_versions(id) NOT NULL
  name              VARCHAR(100) NOT NULL
  quantity          DECIMAL(10,2)
  unit              VARCHAR(30)
  sort_order        INT DEFAULT 0

recipe_version_instructions
  id                SERIAL PRIMARY KEY
  version_id        INT REFERENCES recipe_versions(id) NOT NULL
  step_number       INT NOT NULL
  text              TEXT NOT NULL

stars
  id                SERIAL PRIMARY KEY
  user_id           INT REFERENCES users(id) NOT NULL
  recipe_id         INT REFERENCES recipes(id) NOT NULL
  created_at        TIMESTAMPTZ DEFAULT NOW()
  UNIQUE(user_id, recipe_id)

reviews
  id                SERIAL PRIMARY KEY
  user_id           INT REFERENCES users(id) NOT NULL
  recipe_id         INT REFERENCES recipes(id) NOT NULL
  rating            INT CHECK (rating >= 1 AND rating <= 5)
  comment           TEXT
  created_at        TIMESTAMPTZ DEFAULT NOW()
  UNIQUE(user_id, recipe_id)

tags
  id                SERIAL PRIMARY KEY
  name              VARCHAR(50) UNIQUE NOT NULL

recipe_tags
  recipe_id         INT REFERENCES recipes(id) NOT NULL
  tag_id            INT REFERENCES tags(id) NOT NULL
  PRIMARY KEY(recipe_id, tag_id)

activity
  id                SERIAL PRIMARY KEY
  user_id           INT REFERENCES users(id) NOT NULL
  recipe_id         INT REFERENCES recipes(id) NULL
  action            VARCHAR(50) NOT NULL  -- "fork", "publish", "star", "review"
  metadata          JSONB
  created_at        TIMESTAMPTZ DEFAULT NOW()
```

**Key invariants:**
- `recipe_versions` rows are append-only, never updated or deleted
- `recipe_version_ingredients` and `recipe_version_instructions` are snapshots tied to a version_id
- A recipe's current state = latest version's ingredients + instructions

## Versioning Model

1. Recipe starts at v1.0 (initial creation = first version)
2. Each "publish" increments the minor version (v1.1, v1.2...)
3. Version stores a full snapshot of ingredients + instructions
4. `parent_version_id` links to the version it was derived from
5. Historical versions are never modified

## Forking Model

1. User forks recipe R at version V
2. New recipe created with `forked_from_recipe_id=R`, `forked_from_version_id=V`
3. The fork gets its own independent version chain starting at v1.0
4. Original recipe's version history is untouched

## Diff Algorithm

Compare two versions' ingredient lists and instruction lists:
- **Ingredients:** match by `name`, then diff quantity/unit changes
- **Instructions:** match by position/order, then diff text changes
- **Output:** `{ added: [], removed: [], modified: [] }` for both ingredients and instructions
- Use Python's `difflib` for instruction text diffing (word-level)

## Recipe Similarity

- Build ingredient vectors from recipe versions (unique ingredient names as features)
- Cosine similarity between vectors
- Pre-compute and cache, recompute on version publish
- Display "You might also like" on recipe pages

## API Endpoints

```
Auth:       POST /api/auth/register
            POST /api/auth/login
            POST /api/auth/logout
            GET  /api/auth/me

Users:      GET  /api/users/{username}

Recipes:    GET  /api/recipes
            POST /api/recipes
            GET  /api/recipes/{id}
            PUT  /api/recipes/{id}

Versions:   GET  /api/recipes/{id}/versions
            GET  /api/recipes/{id}/versions/{vid}
            POST /api/recipes/{id}/versions

Fork:       POST /api/recipes/{id}/fork

Lineage:    GET  /api/recipes/{id}/lineage

Diff:       GET  /api/recipes/{id}/diff?v1=X&v2=Y

Stars:      POST /api/recipes/{id}/star
            DELETE /api/recipes/{id}/star

Reviews:    GET  /api/recipes/{id}/reviews
            POST /api/recipes/{id}/reviews

Explore:    GET  /api/explore
            GET  /api/search?q=...

Analytics:  GET  /api/analytics

Similar:    GET  /api/recipes/{id}/similar
```

## Pages (Next.js App Router)

```
/                           — Landing / home
/explore                    — Trending, highest rated, most forked, recent
/recipes/create             — Create recipe form
/recipes/[id]               — Recipe detail (current version)
/recipes/[id]/history       — Version history timeline
/recipes/[id]/diff           — Compare two versions
/recipes/[id]/lineage       — Fork tree graph (React Flow)
/recipes/[id]/fork          — Fork a recipe
/profile/[username]         — User profile + activity
/analytics                  — Platform analytics (Recharts)
```

## Development Phases

### Phase 1 — Foundation
- [x] Docker Compose (PostgreSQL)
- [x] FastAPI skeleton with health endpoint
- [x] SQLAlchemy + sync engine + Alembic wired to app config
- [x] Next.js skeleton with Tailwind
- [x] CORS, env vars, DB connection
- [x] Basic layout (nav, footer, landing page with live backend status)

### Phase 2 — Authentication
- [x] User model + migration
- [x] Registration endpoint (bcrypt)
- [x] Login endpoint (JWT single access token)
- [x] Protected route dependency (`get_current_user`)
- [x] Auth UI (login/register pages + client auth state)
- [x] User profile endpoint
- [x] Backend auth tests (separate `recipeforge_test` DB)

### Phase 3 — Recipes
- [ ] Recipe model + migration
- [ ] Recipe CRUD endpoints
- [ ] Ingredient/instruction models (versioned)
- [ ] Recipe create/edit/view UI
- [ ] Recipe listing page

### Phase 4 — Version Control
- [ ] RecipeVersion model + migration
- [ ] Version creation on publish
- [ ] Snapshot ingredients + instructions per version
- [ ] Version history page
- [ ] Immutability enforcement (no UPDATE/DELETE on versions)

### Phase 5 — Forking
- [ ] Fork endpoint (new recipe from version)
- [ ] Fork attribution fields
- [ ] Fork UI

### Phase 6 — Lineage Graph
- [ ] Lineage endpoint (build tree data)
- [ ] React Flow integration
- [ ] Interactive graph with click-to-open

### Phase 7 — Diff
- [ ] Diff service (ingredient + instruction comparison)
- [ ] Diff endpoint
- [ ] Diff UI with +/- styling

### Phase 8 — Social
- [ ] Stars (toggle, counts)
- [ ] Reviews (rating + comment, averages)
- [ ] Activity feed (events on actions)

### Phase 9 — Explore
- [ ] Explore endpoint (trending, rated, forked, recent)
- [ ] Search (by name, ingredient, cuisine)
- [ ] Explore page UI

### Phase 10 — Profiles
- [ ] Profile page (recipes, forks, stars, activity)

### Phase 11 — Analytics
- [ ] Analytics aggregation queries
- [ ] Recharts visualizations

### Phase 12 — Similarity
- [ ] Ingredient vector builder
- [ ] Cosine similarity service
- [ ] "You might also like" UI

### Phase 13 — Data Science
- [ ] Jupyter notebook or Python script
- [ ] Pandas analysis of recipe popularity factors

### Seed Data
- [ ] 10 users, 20 recipes, versions, forks, reviews, stars
- [ ] Mix of Pakistani + international cuisine
- [ ] Development-only seed script

### Testing
- [ ] Registration, auth, recipe CRUD
- [ ] Version immutability invariant test
- [ ] Forking creates independent lineage
- [ ] Diff correctness
- [ ] Similarity calculations

## Seed Data Recipes

| Recipe | Cuisine | Key Ingredients |
|--------|---------|-----------------|
| Chicken Karahi | Pakistani | Chicken, tomato, green chili, ginger, garlic |
| Biryani | Pakistani | Rice, chicken, yogurt, onion, saffron |
| Chapli Kebab | Pakistani | Beef, onion, tomato, coriander, chili |
| Nihari | Pakistani | Beef, flour, ginger, garlic, garam masala |
| Chicken Handi | Pakistani | Chicken, cream, tomato, onion, cashew |
| Butter Chicken | Indian | Chicken, butter, cream, tomato, spices |
| Ramen | Japanese | Noodles, pork, soy sauce, egg, seaweed |
| Tacos | Mexican | Tortilla, beef, lettuce, tomato, cheese |
| Pasta Carbonara | Italian | Pasta, egg, bacon, parmesan, pepper |
| Smash Burger | American | Beef, bun, cheese, onion, pickles |
| + 10 more varied dishes | | |

## UI Design Principles

- GitHub aesthetic: clean, card-based, monospace accents for version labels
- Code-inspired elements: `v1.2` badges, diff highlighting, branch indicators
- Responsive (mobile-friendly)
- Loading skeletons, empty states, error boundaries, toast notifications
- Dark/light mode (optional, Tailwind `dark:` class)

## Fun Details

- Activity messages like: `feat: added yogurt`, `fix: reduced tomato overload`
- Recipe badges: `Trending`, `Most Forked`, `Experimental`, `Community Favorite`
- These are fun additions, not core functionality

## Key Constraints

- Never store plaintext passwords
- Recipe versions are immutable — no UPDATE/DELETE on `recipe_versions`
- No AI/LLM features
- No over-engineering: stdlib first, fewest files, simplest working solution
- Seed data clearly marked as dev-only

## Future Ideas (DO NOT IMPLEMENT)

- Pull requests for recipe changes
- Collaborative recipe editing
- Recipe collections
- Ingredient substitution engine
- Nutrition analysis
- Grocery-list generation
- Semantic recipe search with embeddings
- Personalized recommendation system
- Recipe "merge conflicts"
- Public developer API
- Mobile app
