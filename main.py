from flagguessr.app.bootstrap import create_game_controller


def main() -> None:
    controller = create_game_controller()
    controller.run()


if __name__ == "__main__":
    main()
