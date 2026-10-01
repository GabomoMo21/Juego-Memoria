# Memory Game

A multi-module **Python memory game** developed as an academic software project. The application includes multiple gameplay components, graphical interfaces, configuration files, ranking data, session persistence, music/assets, and a hall-of-fame system.

The project was developed collaboratively by **Jose Chaves and Gabriel Morales**.

## Highlights

- Python-based game application
- Modular organization across gameplay, menus, ranking, and supporting components
- Local persistence using JSON files
- Hall-of-fame and ranking features
- Configuration and session data management
- Graphical and multimedia assets
- Collaborative development

## Tech Stack

- **Python**
- JSON
- GUI/game interface modules
- File I/O and local persistence
- Git / GitHub

## Repository Structure

```text
Juego-Memoria/
├── main.py
├── clasico.py
├── patrones.py
├── face_gui.py
├── menu_pausa.py
├── halloffame.py
├── hall_of_fame_patrones.py
├── config.json
├── ranking.json
├── ranking_patrones.json
├── session.json
├── Imagenes/
├── Musica/
├── fonts/
└── users_lbph/
```

## Main Features

### Multiple game components

Gameplay is divided into different Python modules rather than being implemented in a single file. This helps separate game modes, menus, ranking logic, and supporting functionality.

### Persistent data

JSON files are used to preserve application state such as configuration, session information, and ranking data between executions.

### Hall of Fame and rankings

The project includes ranking and hall-of-fame functionality for keeping track of player performance across supported game modes.

### Multimedia interface

Images, music, and fonts are stored in dedicated folders, keeping assets separate from the application logic.

## Running the Project

1. Clone the repository:

```bash
git clone https://github.com/GabomoMo21/Juego-Memoria.git
cd Juego-Memoria
```

2. Make sure Python is installed.
3. Install any Python packages required by the imports in the project.
4. Start the application with:

```bash
python main.py
```

## What I Practiced

- Structuring a Python application across multiple modules
- Managing application state with JSON
- Implementing game logic and user-interface flows
- Working with local files and multimedia assets
- Collaborative development with Git/GitHub

## Future Improvements

- Add a `requirements.txt` with exact dependencies
- Add screenshots or a short gameplay demo
- Remove generated/cache files from version control
- Add automated tests for non-GUI game logic
- Document the responsibilities of each module in more detail

## Authors

**Jose Chaves & Gabriel Morales**  
Gabriel's GitHub: [@GabomoMo21](https://github.com/GabomoMo21)
