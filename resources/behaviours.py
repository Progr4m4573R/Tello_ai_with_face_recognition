#These behaviours take place after tello has taken off and is in flight

def search_for_target(tello,target_lost):
    #initialise variables for moving in any direction
    
    while target_lost == True:
        loop_in_a_square(tello)

def loop_in_a_square(tello):
    #This will make the tello fly up and keep looping in a square formation, pausing at intervals to look for a target.
    tello.rotate_clockwise(90)
    tello.move_forward(100)
    tello.rotate_clockwise(90)
    tello.move_forward(100)
    tello.rotate_clockwise(90)
    tello.move_forward(100)
    tello.rotate_clockwise(90)
    tello.move_forward(100)


def patrol(tello):
    tello.move_forward(300)
    tello.rotate_clockwise(180)
    tello.move_forward(300)
    tello.rotate_clockwise(180)


