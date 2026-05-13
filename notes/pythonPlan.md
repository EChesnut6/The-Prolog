Write a Python script that acts as a static site generator for a movie review website.

The script must do the following:

Inputs: Accept a movie title and a custom 'Context' text block.

API Integration: Use the requests library to fetch the movie poster URL, release date, and director from the TMDB API. Use a variable for the API key that I can fill in locally.

Templating: Use a Python f-string or a template file to inject the API data and my custom review into the HTML 'Bones' structure provided previously.

File Output: Save the resulting file as [movie-title].html in a folder named 'reviews'.

Index Generation: Automatically update an index.html file that lists all movies in the 'reviews' folder with links to their individual pages.

Ensure the code is modular so I can easily update the HTML template in the future.