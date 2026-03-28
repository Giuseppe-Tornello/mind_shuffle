# 🇬🇧 Concept
Developing a program useful to students that need to revise their preparation.

The user can:
- Revise: the user can select the subject and/or the topics, the program will show some question (in the form of cards) in casual order and user will be able to answer, after that the card will flip and the user will be able to valutate themselves.
- Import new decks: it will be possible to import new decks trough .json files, by url or by simply pasting the file content.
- Create, edit and delete decks and single cards in each deck

## Technical details

- The code will be entirely written in Python
- Terminal user interface using the [Textual framework](https://textual.textualize.io/)
- Unit-tests will be created
- Every commit will be made with [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
- The whole code will be written by keeping [this article](https://testdriven.io/blog/clean-code-python/) in mind

# How to run

1. Clone this repository:

    ```
    git clone https://github.com/Giuseppe-Tornello/mind_shuffle.git
    cd mind_shuffle/
    ```
2. Create python virtual enviroment

    ```
    python -m venv venv
    ```
3. Activate virtual enviroment
    - Windows:
        ```
        venv\Scripts\activate
        ```
    - Linux / macOS
        ```
        source venv/bin/activate
        # This command might vary depending on your shell type
        ```
4. Install dependecies
    ```
    pip install -r requirements.txt
    ```
5. Run the program
    ```
    python main.py
    ```


# Contributors
- [Kristian Pintaudi](https://github.com/Kristoferz)
- [Giuseppe Tornello](https://github.com/Giuseppe-Tornello)
- [Damiano Trovato](https://github.com/BoredDam)
