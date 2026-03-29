import type { Recipe } from './types';
import recipesData from './recipes.json';

export function getAllRecipes(): Recipe[] {
  return recipesData.recipes as Recipe[];
}

export function getRecipeById(id: string): Recipe | undefined {
  return recipesData.recipes.find((r) => r.id === id) as Recipe | undefined;
}

export function getTotalTime(recipe: Recipe): string {
  const total = recipe.prep_time_minutes + recipe.cook_time_minutes;
  if (total >= 60) {
    const h = Math.floor(total / 60);
    const m = total % 60;
    return m > 0 ? `${h}時間${m}分` : `${h}時間`;
  }
  return `${total}分`;
}

export function getDifficultyLabel(difficulty: number): string {
  const labels = ['', '★☆☆', '★★☆', '★★★'];
  return labels[difficulty] ?? '★☆☆';
}
