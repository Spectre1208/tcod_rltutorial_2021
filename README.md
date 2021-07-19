# Python TCOD Tutorial 2021

#### Link to tutorial: http://rogueliketutorials.com/

###Week 1:

Link to reddit post: https://www.reddit.com/r/roguelikedev/comments/oa2g5r/roguelikedev_does_the_complete_roguelike_tutorial/

####Part 0 & Part 1

No major difference in implementation from the tutorial in the first two parts. The only tweak worth noting is
that I used the context.new() function instead of context.new_terminal() in order to tweak the way the console scales 
on my machine since by default all the characters are really tiny. It would seem that context.new() may be the 
recommended way to initialize the terminal now anyway. 

###Week 2:

Link to reddit post: https://www.reddit.com/r/roguelikedev/comments/oepgnb/roguelikedev_does_the_complete_roguelike_tutorial/

#### Part 2:

I started deviating from the tutorial a bit in part 2. One of the things I wanted to implement in the game is a
"scrollable" map that centers on the player while they explore a much larger world. At the moment I think my
implementation is a bit hack-y; I'm trying to catch up with the weekly tutorial posts, so I just wanted something that 
sort of works and move on with the hope of improving it later...

Essentially what I did was create a new array of tiles that is a subset of the larger game_map tile array that is the
size of the rendered area in the terminal. I called this the "viewport", and pass it to console.tiles_rgb when 
rendering. Since the viewport should be centered on the player, I calculate the viewport origin off of the player's 
position on the game map (for now). Instead of moving the player around the console as is done in the tutorial, I 
move the viewport around the map by passing the dx and dy to a new method in the GameMap object called "scroll_map()" 
whenever the MovementAction is performed. 

I ran into a few challenges with this off the bat that may cause me more trouble down the road:
1. If the edges of the viewport move beyond the game map I get a fatal error that crashes the game that's due to how the
   game map matrix is mapped to the viewport matrix. There may just be a better way to map the viewport but I'll need
   to get more familiar with numpy to figure it out. For now, what I've done is create a "buffer zone" around the core
   map area to prevent the viewport from exceeding the map boundaries. The in_bounds() function now checks against the
   core map boundary. Eventually, I'd like to find a more elegant solution to this in the future.
2. While the player character remains centered on the viewport when moving around the map, stationary entities need to
   move with the viewport. To make this happen I added a couple extra steps before rendering the entities to the
   viewport: First, I calculate the entity's viewport coordinates by subtracting the viewport origin coordinates from
   the entity's map coordinates, then I check to make sure the entity is in view of the viewport with
   0 <= entity_viewport_coords < viewport_width/height. If it is, the entity is rendered to the viewport coordinates.
3. It's tricky to be certain that the game map is being mapped to the viewport correctly. In my initial implementation I
   ran into an issue where the character would run into an invisible wall that was offset from the rendered wall in the
   y direction. I was able to fix this by adding a +1 to the viewport y coordinates, and it appears to have been
   caused by the way I calculate the viewport coordinates to being with (it involves dividing an odd number by 2..).
   I probably need to think of a better way of initializing the viewport, but in general this made me worry about the
   mapping and how player interactions can get decoupled from what is actually rendered to the screen. Hopefully I'll
   be able to straighten this out if I make some time to work through the math fully and get more familiar with the way
   numpy arrays work. 


