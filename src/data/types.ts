export interface IngredientItem {
  name: string;
  amount: number | null;
  unit: string;
  note: string | null;
  grandma_amount?: string;
}

export interface IngredientGroup {
  group: string;
  items: IngredientItem[];
}

export interface Step {
  step: number;
  text: string;
  tip: string | null;
}

export interface Recipe {
  id: string;
  title: string;
  grandmother: {
    name: string | null;
    age: number | null;
    prefecture: string | null;
    city: string | null;
    village: string | null;
    message: string | null;
  };
  region: {
    area: string;
    prefecture_code: string;
    prefecture: string;
  };
  meta: {
    created_at: string;
    is_featured: boolean;
    is_endangered: boolean;
  };
  category: string;
  tags: string[];
  season: string[];
  servings: number;
  prep_time_minutes: number;
  cook_time_minutes: number;
  difficulty: number;
  story: string;
  ingredients: IngredientGroup[];
  steps: Step[];
  grandma_notes: string | null;
  cultural_background: string | null;
  photos: {
    main: string | null;
    thumbnail: string | null;
  };
  related_recipe_ids: string[];
  thumbnail_emoji: string;
  episode: string | null;
  source: {
    types: string[];
    contributor: string | null;
  };
}

export interface RecipesData {
  recipes: Recipe[];
}
