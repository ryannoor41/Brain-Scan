from gui import draw_loading_animation
from gui import App
import turtle

if __name__ == "__main__":
    # Loading animation
    turtle.tracer(0)  # Turn off auto-drawing
    draw_loading_animation()
    turtle.update()  # Update the screen one final time

    # Close the Turtle graphics window
    turtle.bye()
    # Run The App
    app = App()
    app.mainloop()