#!/usr/bin/env python

from bin.compare_ingredients import RecipeDataset
from flask import Flask
from flask import render_template
import sys

THRESHOLD = .3

app = Flask(__name__)

# load dataset
recipe_file = '../recipe_scraping/data/smitten_kitchen_ingredients.jl'
recipe_dataset = RecipeDataset(recipe_file, sameness_threshold=THRESHOLD)

@app.route('/')
def list_recipes():
    recipes = [r for r in recipe_dataset.values()]
    return render_template('recipe_list.html', recipes=recipes)

@app.route('/recipes/<recipe_id>')
def show_similar_recipes(recipe_id):
    related = recipe_dataset.get_related_recipes(recipe_id)[:20]
    return render_template('recommended_recipes.html', related=related)
