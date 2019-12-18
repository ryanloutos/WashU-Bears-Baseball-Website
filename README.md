Baseball-Pitching-Portal
Collaborators: Ryan Loutos, Mitchell Black, Brian Hall

The project structure and login pages were learned and/or taken from 
https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
The blog walks through setting up a flask app for someone with no experience and was used 
to get the ball rolling

To do
- Go through code and make sure everything is neat and organized where it is at
- Get debugger working for vscode
- Make the function documentation things
- Add basic baseball stat division(hits, walks, ...)
- summary stats by game(player home page)
- game selected summary stats(able to choose outings to compare/ over time)
- whole team comparison and global tables
- tracking individual pitches over a season


Ideas for improvement
- Make num_pitches automatic
- Make count_balls and count_strikes automatic
- Improve little data entry things
- Figure out way to make data entry fast and easy
- Make default seasons to choose from
- Create a filter so you can choose to see cumulative data for team and/or individual pitchers over a certain time, season, etc.
- Make a neat, clean, easy to read summary page for any outing(s)

Currently being worked on:
- Creating a csv entry point for pitch information
  - TODO:
    - more file validation points
    - make sure when saving that temp file names are not duplicated
    - safety checks for file existence
    - Add auto-index for outs
    - account for user input mistakes (spaces, capitals, strings vs numbers)
    - improve instruction set of upload file
  - DONE:
    - Auto index for pitches and counts
    - It is possible to upload outings via CSV and have them saved to database



Cool README.md style stuff [here](https://help.github.com/en/github/writing-on-github/basic-writing-and-formatting-syntax)