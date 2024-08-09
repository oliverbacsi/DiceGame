# Dice Game
Dice Game on ANSI terminal in Python

---

> ++Note++ : You need an ANSI capable terminal with 256 colors to run this program.  
> All the screen drawing, cursor positioning, coloring are using ANSI.

![Screenshot](https://github.com/oliverbacsi/DiceGame/blob/main/Screenshot.png)

---

#### Game Rules

This game makes only sense to play in a group (possibly at least 5 people to guarantee some fun).  
Initially all players get the same amount of playing dice, the dice represent the "lives" of the player. Also one player is selected as "the first speaker".  
In each round all players roll all their (remaining) dice, covering them with their palms not to be seen by others, so that each player only has information about his/her own dice (just like in poker, You only see Your own cards).  
Knowing the values on the own dice and the total amount of dice still in game, the actual "speaker" has to place a bet about the total amount of a certain value on all dice in game.  

> For example : **`10pcs of 5`** -- meaning: 'I bet there are at least 10pcs of "5" values on all our dice still in game'.  

> ++Important++ : The players can only place a bet on the amount of the `2`,`3`,`4`,`5`,`6` values, these are the "regular" values.  
> The `1` is a **Jolly Joker** : You can not place a bet on the amount of 1's, but the quantity of 1's adds up with the quantity of the value the bet was placed for.  
> So in reality **`10pcs of 5`** means : I bet the total number of 5's and 1's is at least 10 on all our dice still in game

Now the next player will be the next speaker, and now this player has two options:  

1. Raise the bet further, for example to tell : `11pcs of 2` -- 'I bet the total number of 2's and 1's is at least 11'  
	- The player can raise either the quantity, or keep the same quantity but raise the value.
	- Quantity can not go downwards.
	- Value can go downwards IF quantity is raised at the same time.  
2. If the speaker player suspects that the previous player made a bet too high, then instead of raising further, the current speaker player says **`block!`** to stop the further bets and make a reality check.
	- Now there comes the moment of truth: All players reveal all their dices and they count the total quantity of the value in bet plus the 1's.  
	- They check who was right and who was wrong and the player who was wrong loses a dice:
		- If there was at least that many matching dice (the bet turned out to be right), the blocking player loses.
		- If there was less matching dice than the quantity in the bet (the bet was too high and the blocking player was right to block), the player with the last (too high) bet loses a dice.
	- The next speaker will be the player after the one who said `block`.

If one player loses all his/her dice (all his/her life) the player is out from the game, the others keep playing.  
So each turn there are less and less dice in game until the point when only one player is left standing -- this player is the winner of the game.  
You can classify all other players in a reverse sequence how soon they fell out from the game.

---

#### Game controls

At the start some initial data are asked: how many players in game, how many initial dice per player, what is the name of the Human Player, and which position the Human Player would like to be in the player's list.  
Except for the Human Player, all other players are controlled by an automated algorhythm. To represent a different playing behaviour of the AI players, there is a different willingness for "risky" play assigned to each AI player. So some will play a safe game while some others will risk more, just like in real life. This is to eliminate a boring game where the bets of the AI players are pretty much predictable.  
During the game the AI players are playing automatically, and when it's the Human Player's turn then an input prompt is given:  

- The player either has to type two numbers: `5 6` meaning "5pcs of 6's and 1's"
- Or the player types `block` or `blk` or `b` meaning to block the previous bet

In case there is a pop-up window, there is an `[ENTER]` text in the corner, meaning the player needs to hit the 'ENTER' key to move on.

---

#### Main Screen Elements

- In the first column the player's names are listed
	- The speaker player is highlighted with blue background and a small arrow at the start of the line
- In the next column there are the remaining dice displayed
	- After rolling the dice show a random color pattern, symbolizing that they have random values. The colors do not represent the values, they are totally random.
	- Only the dice of the human player are displayed with values
	- When a "block" is called, all dice will be revealed with values, and they change their colors to match their values to be able to count easier (although the program will do it anyway)
- In the last column the last bets of the players are recorded with sequentially fading color based on how old the bet is
- In the top-right corner the number of remaining dice in game is displayed in square braces to assist Your bet decision
- If it's Your turn, the input prompt is displayed below the list of players
- Pop-up windows appear in the middle of the terminal window

---

#### TODO:

- [ ] The bets of the AI players should not always start from 1 and step by 1, but if the expected number of a bet value is much higher, then the AI players could raise more courageously.
