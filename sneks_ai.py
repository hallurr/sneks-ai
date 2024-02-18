import numpy as np
import random

class Snake:
    def __init__(self, 
                 head, 
                 body):
        self.head = head
        self.body = body
        self.alive = True
        self.score = 0
        self.scoreUpdate = 0
        self.hunger = 0
        
    def take_action(self, 
                    game_state, 
                    choices):
        # take in the game board and output is action
        # start with random brain (later the brain will be a neural network)
        
        # state = game.get_state() # Later this self.canvas_size x self.canvas_size x 3 matrix will be the input to the neural network
        possible_actions = choices
        
        action = random.randint(0, len(possible_actions)-1)  # Choose a random action
        return action
    
class Apple:
    def __init__(self, 
                 position, 
                 value, 
                 decay_rate):
        self.position = position
        self.value = value
        self.decay_rate = decay_rate
        
    def update_value(self):
        self.value = self.value*self.decay_rate

class SnakeGame:
    # snake dies if it hits walls
    # snake dies if it hits itself
    # snake grows when it eats food
    # food is randomly placed, not on the snake
    # game ends when snake dies
    # score goes up by gamma*ticker when snake eats food (ticker starts at 1, gamma is 0.98)
    # ticker goes up by 1 for every step, starting at 1
    # ticker is reset to 1 when snake eats food
    def __init__(self, 
                 canvas_size = 20, 
                 nSnakes = 1, 
                 nApples = 5, 
                 dimensions = 2, 
                 step_Reward = -1, 
                 apple_Reward = 255, 
                 snakebody_Reward = 100, 
                 snake_dieHunger = 50, 
                 snake_dieReward = -100,
                 gamma = 0.98, 
                 max_ticks = 1000, 
                 annotate = False,
                 keepGameLog = False):
        
        # Game init
        self.keepGameLog = keepGameLog
        self.canvas_size = canvas_size
        self.max_ticks = max_ticks
        self.dimensions = dimensions
        self.annotate = annotate
        self.gamma = gamma
        self.available_directions()
        
        # Rewards init
        self.nApples = nApples
        self.apple_Reward = apple_Reward
        self.step_Reward = step_Reward
        self.snakebody_Reward = snakebody_Reward
        self.snake_dieReward = snake_dieReward
        
        # Snake init
        self.nSnakes = nSnakes
        self.snake_dieHunger = snake_dieHunger
        
        # Gameboard init
        self.reset()
        
        
    # Function to define all possible directions        
    def available_directions(self):
        # Define all possible directions     
        # just start with 2D and complicate later
        if self.dimensions == 2:
            self.directions = {
                'North': [0, -1],
                'South': [0, 1],
                'East': [1, 0],
                'West': [-1, 0]
            }
            
        if self.dimensions == 3:
            self.directions = {
                'North': [0, -1, 0],
                'South': [0, 1, 0],
                'East': [1, 0, 0],
                'West': [-1, 0, 0],
                'Up': [0, 0, -1],
                'Down': [0, 0, 1]
            }
            
        self.choices = list(self.directions.keys())
           
            
    # Function to reset the gameboard
    def reset(self):
        self.done = False
        self.ticker = 1
        self.occupied_space = np.zeros((self.canvas_size, self.canvas_size))
        self.initializeSnakes()        
        self.apples = dict()
        for i in range(self.nApples):
            apple_pos = self.place_apple()
            self.apples[i] = Apple(apple_pos, self.apple_Reward, self.gamma)
        
        if self.keepGameLog:
            self.gameLog = dict()
            self.gameLog['state_0'] = self.get_agnosticState()
    
    # Function to initialize the snakes
    def initializeSnakes(self):
        self.snakes = dict()
        for i in range(self.nSnakes):
            # randomize the starting position of the enemy snakes, and their heading
            randomheading = self.directions[random.choice(self.choices)]
            randomhead = [random.randint(3, self.canvas_size-4), random.randint(3, self.canvas_size-4)]
            body = [[randomhead[0]-1*randomheading[0], randomhead[1]-1*randomheading[1]],\
                    [randomhead[0]-2*randomheading[0], randomhead[1]-2*randomheading[1]]]
            # make sure the enemy snakes spawn where randomhead and body xy coordinates are [0,0,0]
            
            while self.occupied_space[randomhead[0], randomhead[1]] == 1 or self.occupied_space[body[0][0], body[0][1]] == 1 or self.occupied_space[body[1][0], body[1][1]] == 1:
                randomhead = [random.randint(0, self.canvas_size-1), random.randint(0, self.canvas_size-1)]
                body = [[randomhead[0]-1*randomheading[0], randomhead[1]-1*randomheading[1]],\
                    [randomhead[0]-2*randomheading[0], randomhead[1]-2*randomheading[1]]]
            
            self.occupied_space[randomhead[0], randomhead[1]] = 1
            self.occupied_space[body[0][0], body[0][1]] = 1
            self.occupied_space[body[1][0], body[1][1]] = 1
            self.snakes[i] = Snake(head = randomhead, body = body)
    
    # Function to place an apple
    def place_apple(self):
        apple_pos = [random.randint(0, self.canvas_size-1), random.randint(0, self.canvas_size-1)]
        # check if the state of the gameboard at the apple location is 0, if not, place the apple somewhere else
        while self.occupied_space[apple_pos[0], apple_pos[1]] == 1:
            apple_pos = [random.randint(0, self.canvas_size-1), random.randint(0, self.canvas_size-1)]
        self.occupied_space[apple_pos[0], apple_pos[1]] = 1
        return apple_pos
        
    # Function to update the score and the apple position  
    def apple_eaten(self, 
                    snakeID, 
                    applenum, 
                    eaten):
        if eaten:
            self.snakes[snakeID].score += (self.gamma**self.ticker)*self.apple_Reward + self.step_Reward
            self.snakes[snakeID].scoreUpdate += (self.gamma**self.ticker)*self.apple_Reward + self.step_Reward
            self.snakes[snakeID].hunger = 0
            # self.score += (self.gamma**self.ticker)*self.apple_Reward + self.step_Reward
            # self.score_update = (self.gamma**self.ticker)*self.apple_Reward + self.step_Reward
            # self.ticker = 1
            new_apple_pos = self.place_apple()
            self.apples[applenum] = Apple(new_apple_pos, self.apple_Reward, self.gamma)
        else:
            self.snakes[snakeID].score += self.step_Reward
            self.snakes[snakeID].scoreUpdate += self.step_Reward
            self.snakes[snakeID].hunger += 1
            # self.score += self.step_Reward
            # self.score_update = self.step_Reward
            # self.ticker += 1
        
    # Function to update the heading of the snake
    def update_heading(self, 
                       action):
        if action < 0 or action >= len(self.choices):
            raise ValueError("Invalid action")
        return self.directions[self.choices[action]]
    
    def snake_died(self, 
                   snakeID):
        self.snakes[snakeID].alive = False
        self.snakes[snakeID].scoreUpdate += self.snake_dieReward
    
    # Function to check if the snake hit itself
    def check_hitSelf(self, 
                      possiblenewhead, 
                      snakeID):
        # check for given snake if he hit own body, then he is dead
        if possiblenewhead in self.snakes[snakeID].body:
            if self.annotate:
                print(f"Self hit, {snakeID} died!")
            self.snake_died(snakeID)
            return True
        return False

    # Function to check if the snake hit the wall
    def check_hitWall(self, 
                      possiblenewhead, 
                      snakeID):
        if possiblenewhead[0] < 0 or possiblenewhead[0] >= self.canvas_size or possiblenewhead[1] < 0 or possiblenewhead[1] >= self.canvas_size:
            if self.annotate:
                print(f"Wall hit, {snakeID} died!")
            self.snake_died(snakeID)
            return True
        return False
    
    # Function to check if the snake hit another snake, head on head (both die)
    def check_headCollision(self, alivesnakes, possiblenewheads):
        # list all snakes and check if their heads are in the same position
        for head_1 in range(len(possiblenewheads)):
            for head_2 in range(head_1+1, len(possiblenewheads)):
                if possiblenewheads[head_1] == possiblenewheads[head_2]:
                    self.snake_died(alivesnakes[head_1])
                    self.snake_died(alivesnakes[head_2])
                    if self.annotate:
                        print(f"Head on head collision, {alivesnakes[head_1]} and {alivesnakes[head_2]} died!")
                    
    # Function to check if the snake hit another snake, head on body (eating body)
    def check_eatingBody(self, 
                         snakeID, 
                         alivesnakes):
        # check if any bodypart of any alive snake is in the same position as the head of the snakeID snake
        othersnakes = [snake for snake in alivesnakes if snake != snakeID]
        for othersnake in othersnakes:
            if self.snakes[snakeID].head in self.snakes[othersnake].body:
                # get the index and maxindex of the bodypart that is in the same position as the head of the snakeID snake
                snakebodylength = len(self.snakes[othersnake].body)
                snakebodyindex = self.snakes[othersnake].body.index(self.snakes[snakeID].head)
                # remove the bodyparts of the other snake that are in the same position as the head of the snakeID snake and over
                self.snakes[othersnake].body = self.snakes[othersnake].body[:snakebodyindex]
                self.snakes[othersnake].scoreUpdate -= self.snakebody_Reward*(snakebodylength - snakebodyindex)
                if len(self.snakes[othersnake].body) == 0:
                    self.snake_died(othersnake)
                self.snakes[snakeID].score += self.snakebody_Reward*(snakebodylength - snakebodyindex)
                self.snakes[snakeID].scoreUpdate += self.snakebody_Reward*(snakebodylength - snakebodyindex)
            
    # Function to get the state of the game as a matrix (viewpoint of the given snakeID)
    def get_state(self, 
                  snakeID):
        
        if self.snakes[snakeID].alive == False:
            return None
        
        state = np.zeros((self.canvas_size, self.canvas_size, 3), dtype=np.uint8)
        
        for snakeIDS in self.snakes:
            if snakeIDS != snakeID:
                if self.snakes[snakeIDS].alive:
                    state[self.snakes[snakeIDS].head[0], self.snakes[snakeIDS].head[1], 2] = 255
                    for part  in self.snakes[snakeIDS].body:
                        state[part [0], part [1], 2] = 175
            else:
                state[self.snakes[snakeIDS].head[0], self.snakes[snakeIDS].head[1], 1] = 255
                for part  in self.snakes[snakeIDS].body:
                    state[part [0], part [1], 1] = 175
        
        for apple in self.apples:
            state[self.apples[apple].position[0], self.apples[apple].position[1], 0] = 255
        
        return state
    
    def get_agnosticState(self):
        state = np.zeros((self.canvas_size, self.canvas_size, 3), dtype=np.uint8)
        alivesnakes = [snake for snake in self.snakes if self.snakes[snake].alive]
        for snakeIDS in alivesnakes:
            state[self.snakes[snakeIDS].head[0], self.snakes[snakeIDS].head[1], 1] = 255 - 0.5*255*(self.snakes[snakeIDS].hunger/self.snake_dieHunger)
            for part  in self.snakes[snakeIDS].body:
                state[part [0], part [1], 1] = 175-0.5*175*(self.snakes[snakeIDS].hunger/self.snake_dieHunger)
        
        for apple in self.apples:
            state[self.apples[apple].position[0], self.apples[apple].position[1], 0] = 255-0.5*255*(self.apples[apple].value/self.apple_Reward)
        
        return state
    
    
    # Function to update the occupied space (simplified version of get_state, only 2D and no colors, just 0 and 1)
    def update_occupied_space(self):
        state = np.zeros((self.canvas_size, self.canvas_size), dtype=np.uint8)
        alivesnakes = [snake for snake in self.snakes if self.snakes[snake].alive]
        
        for snake in alivesnakes:
            state[self.snakes[snake].head[0], self.snakes[snake].head[1]] = 1
            for part in self.snakes[snake].body:
                state[part[0], part[1]] = 1
        
        for apple in self.apples:
            state[self.apples[apple].position[0], self.apples[apple].position[1]] = 1
        
        self.occupied_space = state
       
    # Function to check if the game is over (max ticks reached or all snake dead)
    def check_game_over(self):
        # check if the game is over
        if self.ticker > self.max_ticks:
            if self.annotate:
                print("Game over, max ticks reached")
            self.done = True
            return True
        
        if all([not self.snakes[snake].alive for snake in self.snakes]):
            if self.annotate:
                print("Game over, all snakes dead")
            self.done = True
            return True
        
        return False
    
    def hunger_update(self, 
                      snakeID):
        self.snakes[snakeID].hunger += 1
        if self.snakes[snakeID].hunger > self.snake_dieHunger:
            self.snake_died(snakeID)
            return True
        return False
    
    
    def get_totalScores(self):
        return [self.snakes[snake].score for snake in self.snakes]
    
    
    def update_snake_position(self,
                              snakeID,
                              appleID, 
                              newheadpos, 
                              ate_apple):
        previoushead = self.snakes[snakeID].head.copy()
        previousbody = self.snakes[snakeID].body.copy()
        newhead = newheadpos.copy()
        if ate_apple:
            self.apple_eaten(snakeID, appleID, True)
            # lengthen the snake
            self.snakes[snakeID].body = [previoushead] + previousbody
            self.snakes[snakeID].head = newhead
        else:
            self.snakes[snakeID].body = [previoushead] + previousbody[:-1]
            self.snakes[snakeID].head = newhead
            self.apple_eaten(snakeID, appleID, False)
    
    def collision_Checks(self,
                         alivesnakes,
                         possiblenewheads):
        # check if anyone died due to bonking heads together
        self.check_headCollision(alivesnakes, possiblenewheads)
        # check if anyone died due to hitting wall, hitting itself, or hunger
        for i in range(len(alivesnakes)):
            if not self.snakes[alivesnakes[i]].alive:
                continue
            if self.check_hitSelf(possiblenewheads[i], alivesnakes[i]):
                continue
            if self.check_hitWall(possiblenewheads[i], alivesnakes[i]):
                continue
            if self.hunger_update(alivesnakes[i]):
                continue
    
    def updateGame(self, 
                   action_vector):
        
        # Update all apple values
        for apple in self.apples:
            self.apples[apple].update_value()
            # if the apple value is less that 25% of the original value, place a new apple
            if self.apples[apple].value < 0.25*self.apple_Reward:
                new_apple_pos = self.place_apple()
                self.apples[apple] = Apple(new_apple_pos, self.apple_Reward, self.gamma)
        
        # Update the ticker
        self.ticker += 1
        
        if self.keepGameLog:
            self.gameLog[f'state_{self.ticker}'] = self.get_agnosticState()
        
        for snake in self.snakes:
            self.snakes[snake].scoreUpdate = 0
        
        
        # 1: list snakenames that are alive and Calculate new head positions
        alivesnakes = [snake for snake in self.snakes if self.snakes[snake].alive]
        actions = [action_vector[snake] for snake in self.snakes if self.snakes[snake].alive]
        possiblenewheads = [[self.snakes[snake].head[0] + self.directions[self.choices[actions[i]]][0], self.snakes[snake].head[1] + self.directions[self.choices[actions[i]]][1]] for i, snake in enumerate(alivesnakes)]
                
        # 2. Perform all collision checks
        self.collision_Checks(alivesnakes = alivesnakes, possiblenewheads = possiblenewheads)
            
        for i, snakeID in enumerate(alivesnakes):
            if self.snakes[snakeID].alive:
                # Determine if the snake eats an apple or just moves
                ate_apple = possiblenewheads[i] in [self.apples[apple].position for apple in self.apples]
                appleID = None
                if ate_apple:
                    appleID = [apple for apple in self.apples if self.apples[apple].position == possiblenewheads[i]][0]
                self.update_snake_position(snakeID, appleID, possiblenewheads[i], ate_apple)
                
        # Check if any head collided with any body
        for i, snakeID in enumerate(alivesnakes):
            self.check_eatingBody(snakeID, alivesnakes)
        
        # make a vector of the rewards for each snake (even the dead ones)
        reward_vector = [self.snakes[snake].scoreUpdate for snake in self.snakes]
        done_vector = [not self.snakes[snake].alive for snake in self.snakes]
        
        
        if self.check_game_over():
            self.done = True
        
        return self.get_agnosticState(), reward_vector, done_vector
        