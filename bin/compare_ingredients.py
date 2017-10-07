#!/usr/bin/env python

import itertools
import json
from lib.ingredient_cleaning import apply_pipeline

def overlap_distance(a, b):
    a, b = set(a), set(b)
    return 1.0 * len(a.intersection(b)) / len(a.union(b))

def make_ngrams(s, n=2):
    s = iter(s)
    ngrams = []
    while True:
        ngram = list(itertools.islice(s, n))
        if not ngram:
            break
        ngrams.append(''.join(ngram))
        #
    return ngrams

def string_bigrams(s):
    ret = []
    for word in s.split(' '):
        grams = make_ngrams(word)
        ret += grams
    return ret

def string_distance(s1, s2):
    return overlap_distance(
        string_bigrams(s1), string_bigrams(s2))

def ingredient_vector_comparison(recipe1, recipe2):
    distance_tracker = {}
    for r1 in recipe1:
        for r2 in recipe2:
            distance = string_distance(r1, r2)
            if r2 not in distance_tracker:
                distance_tracker[r2] = (r1, distance)
            else:
                if distance > distance_tracker[r2][1]:
                    distance_tracker[r2] = (r1, distance)
    return distance_tracker

def score_matches(recipe1, recipe2, sameness_threshold=.2):
    r1_length, r2_length = len(recipe1), len(recipe2)
    matches = ingredient_vector_comparison(recipe1, recipe2)
    matched = 0
    for k in matches:
        if matches[k][1] > sameness_threshold:
            matched += 1
    match_score = float(matched) / (r1_length + r2_length - matched)
    matches['match_score'] = match_score
    return matches


if __name__ == '__main__':
    with open('test_input.json') as f:
        first = json.load(f)
        first['ingredients'] = [apply_pipeline(s) for s in first['ingredients']]
        print("FIRST RECIPE")
        print(json.dumps(first, indent=4))

    with open('recipe_scraping/data/smitten_kitchen_ingredients.jl') as f:
        matches_list = []
        for recipe in f:
            r = json.loads(recipe)
            r['ingredients'] = [apply_pipeline(s) for s in r['ingredients']]
            matches = score_matches(first['ingredients'], r['ingredients'], .3)
            matches['title'] = r['title'][0]
            matches['url'] = r['url']
            matches_list.append(matches)

        for m in sorted(matches_list, key=lambda match: -1 * match['match_score'])[1:]:
            print(json.dumps(m, indent = 4))
