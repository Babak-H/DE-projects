{% macro generate_film_ratings() %}

WITH films_with_ratings AS (
    SELECT 
        film_id,
        title,
        release_date,
        price,
        rating,
        user_rating,
        -- {{ classify_ratings(user_rating) }}
        CASE
            WHEN user_rating >= 4.5 THEN 'Excellent'
            WHEN user_rating >= 4.0 THEN 'Good'
            WHEN user_rating >= 3.0 THEN 'Average'
            ELSE 'Poor'
        END as rating_category
    FROM {{ ref('films') }}
),

films_with_actors AS (
    SELECT
        f.film_id,
        f.title,
        STRING_AGG(a.actor_name, ', ') AS actor -- Aggregating actor names for each film
        FROM {{ ref('films') }} AS f
        LEFT JOIN {{ ref('film_actors') }} fa ON f.film_id = fa.film_id
        LEFT JOIN {{ ref('actors') }} a ON fa.actor_id = a.actor_id
        GROUP BY f.film_id, f.title
)

SELECT 
    fwr.*,
    fwa.actors
FROM films_with_ratings fwr
LEFT JOIN films_with_actors fwa 
ON fwr.film_id = fwa.film_id



{% endmacro %}