

def showFlag(screen, flags ,current_country, width,  height, flag_size,):
        screen.fill((0, 0, 0))  # Set background color to black
        screen.blit(flags[current_country], (width // 2 - flag_size[0] // 2, height // 2 - flag_size[1] // 2))