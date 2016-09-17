#----- IFN680 Assignment 1 -----------------------------------------------#
#  The Wumpus World: a probability based agent
#         (the function next_room_prob)
#
#-----Statement of Authorship----------------------------------------#
#
#  By submitting this code I agree that it represents my own work. 
#  I am aware of the University rule that a student must not act in 
#  a manner which constitutes academic dishonesty as stated and 
#  explained in QUT's Manual of Policies and Procedures, Section C/5.3
#  "Academic Integrity" and Section E/2.1 "Student Code of Conduct".
#
#    Student no: n8635307
#    Student name: Ba Hoang An Nguyen
#
#--------------------------------------------------------------------#

from random import *
from IFN680_AIMA.logic import *
from IFN680_AIMA.utils import *
from IFN680_AIMA.probability import *
import tkMessageBox,time

#__________________________________________________________________________________________________________________________    
#___________________________________________________________________________________________________________________________    
#---------------------------------------------------------------------------------------------------------------------------
    #
    #  The following two functions are to be developed by you. They are functions in class Robot. If you need,
    #  you can add more functions in this file. In this case, you need to link these functions at the beginning
    #  of class Robot in the main program file the_wumpus_world.py.
    # 
#---------------------------------------------------------------------------------------------------
    #
    # For this assignment, we treat a pit and the wumpus equally. Therefore, each room has two states. One state is 'empty',
    # the other state is 'containing a pit or the wumpus'. Thus, we can use a Boolean variable to represent each room,
    # value 'True' means the room contains a pit/wumpus, value 'False' means the room is empty.
    #
    # For a cave with n columns and m rows, there are totally n*m rooms, i.e, we have n*m Boolean variables to represent the rooms.
    # A configuration of pits/wumpus in the cave is an event of these variables. Without restricting the number of pits, totally
    # there are 2 to the power of n*m possible configurations.
    # For example, for a cave with 2 columns and 2 rows, the cave has 4 rooms, there are 16 configurations, (True, True, True, True)
    # is one configuration meaning all rooms are occupied by a pit/wumpus, and (True, False, False, False) is another configuration
    # where only one room has a pit/wumpus, the other three rooms are empty.
    #
    # The function PitWumpus_probability_distribution() below is to construct the joint probability distribution of all possible
    # pits/wumpus configurations in a given cave. The two parameters, width and height, are the number of columns and the number
    # of rows in the cave, respectively. In this function, you can create an object of JointProbDist to store the joint probability
    # distribution. will be used by your function next_room_prob() below to calculate the required probabilities.
    #
    # This function will be called in the constructor of class Robot in the main program the_wumpus_world.py to construct the
    # joint probability distribution object. Your function next_room_prob() will need to use the joint probability distribution
    # to calculate the required conditional probabilities.
    #
    
def PitWumpus_probability_distribution(self, width, height):
    #set probability == 0 for inconsistent events
    #testing probability threshold (default == 0)
    T, F = True, False

    p_true = 0.2 # having wumpus or pit
    p_false = 1 - 0.2 # not having

    #Generate N rooms
    N = width * height

    pitwumpus_variables = []

    # for i in range(1,N+1):
    #     pitwumpus_variables = pitwumpus_variables + ['R'+ str(i)]

    for i in range(1, width+1):
        for j in range(1, height+1):
            pitwumpus_variables = pitwumpus_variables + ["({0},{1})".format(i, j)]

    #Specify the values for each room
    room_values = {}
    for each in pitwumpus_variables:
        room_values[each] = [True,False]
        # print each, room_values[each],'\n'

    #Create an object of JointProDist
    Pr_N_rooms = JointProbDist(pitwumpus_variables, room_values)

    #Generate all possible events
    knownPW = self.observation_pits(self.visited_rooms)

    events = all_events_jpd(Pr_N_rooms.variables, Pr_N_rooms, {})

    # #Assign probability for each event
    for each_event in events:
        print each_event
        prob = 1
        for (var, val) in each_event.items():
            if val == F:
                prob = prob * p_false
            else:
                prob = prob * p_true
        Pr_N_rooms[each_event] = prob

    # for k,v in Pr_N_rooms.prob.items():
    #     print k, "--", v

    # print Pr_N_rooms[0]
    # print Pr_N_rooms.show_approx()


    return Pr_N_rooms
#---------------------------------------------------------------------------------------------------
    #
    #  For the function next_room_prob() below, the parameters, column and row, are the robot's
    #  current position (column,row) in the cave environment. This function is to find the next
    #  room for the robot to go. There are three cases:
    #
    #    1. Firstly, you may like to call the function check_safety() of class Robot to find a
    #       safe room. If there is a safe room, return the location (column,row) of the safe room.

    #    2. If there is no safe room, this function needs to choose a room whose probability of containing
    #       a pit/wumpus is lower than a pre-specified probability threshold, then return the location of
    #       that room.

    #    3. If the probabilities of all the available rooms are not lower than the pre-specified probability
    #       threshold, return (0,0).
    #
def next_room_prob(self, column, row):
    #    1. Firstly, you may like to call the function check_safety() of class Robot to find a
    #       safe room. If there is a safe room, return the location (column,row) of the safe room.
    pre_room = (0,0)
    query_rooms = set()
    # Get surrounding rooms of the position (column,row), which are potential rooms to explore

    #Checking surrounding rooms to see if there is any 100% safe room, if yes return the room.
    new_safe_room = None

    surroundings = self.cave.getsurrounding(column, row)
    for each_s in surroundings:
        if each_s not in self.visited_rooms:
            if self.check_safety(each_s[0],each_s[1]): ## method check_safety() does a propositional-logic resolution reasoning to
                                                        ## determine whether moving to position each_s is safe or not
                new_safe_room = each_s ## if it is safe, return this room, otherwise return (0,0)
                return new_safe_room
            else:
                query_rooms.add(each_s)

    #    2. If there is no safe room, this function needs to choose a room whose probability of containing
    #       a pit/wumpus is lower than a pre-specified probability threshold, then return the location of
    #       that room.

    knownPW = self.observation_pits(self.visited_rooms)
    knownBS = self.observation_breeze_stench(self.visited_rooms)

    lowest_prob = (1,0)
    lowest_risk_room = None
    for each_query_room in query_rooms:
        query_prob = (0,0) #(T,F)
        all_possible_events = all_events_jpd(self.Pr_N_rooms.variables, self.Pr_N_rooms, {})

        false_events_sum = 0
        true_event_sum = 0
        for each_event in all_possible_events:
            filter = each_event.viewitems() >= knownPW.viewitems()
            # filter &= each_event["({0},{1})".format(each_query_room[0], each_query_room[1])] == False
            if filter == False:
                continue

            consisten_event = set(query_rooms)
            consisten_event_value = {}
            for each_fringe in consisten_event:
                consisten_event_value["({0},{1})".format(each_fringe[0], each_fringe[1])] = each_event["({0},{1})".
                    format(each_fringe[0], each_fringe[1])]
            isConsistent = self.consistent(knownBS, consisten_event_value)
            # if isConsistent == 1:
            #     print "consisten = 1"
            temp = self.Pr_N_rooms[each_event] * isConsistent

            if each_event["({0},{1})".format(each_query_room[0], each_query_room[1])] == True:
                true_event_sum += temp
            else:
                false_events_sum += temp

        query_prob = (true_event_sum, false_events_sum)

        # query_prob = 1 - query_prob #calculate the probability of pit/wumpus
        print "current room: ", each_query_room[0], each_query_room
        print "before normalization: ", query_prob[0], ", ", query_prob[1]

        normalization_number = 1 / (query_prob[0] + query_prob[1])
        normalized_true_event_prob = normalization_number * query_prob[0]
        normalized_false_event_prob = normalization_number * query_prob[1]
        query_prob = (normalized_true_event_prob, normalized_false_event_prob)

        print each_query_room, "--", query_prob
        if query_prob[0] <= lowest_prob[0]:
            lowest_prob = query_prob
            lowest_risk_room = each_query_room

    print "Lowest prob room info: ", lowest_risk_room, "--", lowest_prob
    # min_prob_room = self.max_pit_probability
    # row = 0
    # col = 1
    #
    # for each_s in surroundings:
    #     print " "
    #     if min_prob_room > enumerate_joint_ask(each_s, {}, PitWumpus_probability_distribution()):
    #         min_prob_room = enumerate_joint_ask(each_s, {}, PitWumpus_probability_distribution())
    #         new_room = (each_s[0],each_s[1])

    #    3. If the probabilities of all the available rooms are not lower than the pre-specified probability
    #       threshold, return (0,0).
    if lowest_prob[0] == 1:
        return pre_room
    return lowest_risk_room

    tkMessageBox.showinfo("Not yet complete", "You need to develop the function next_room_prob.")