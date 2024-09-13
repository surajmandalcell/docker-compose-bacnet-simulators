# SE8350 Room Controller Simulation

This project simulates a Schneider Electric SE8350 Room Controller using BACnet/IP protocol.

## Project Structure

```
/
├── docker-compose.yml
├── README.md
├── requirements.txt
└── se8350_controller/
    ├── Dockerfile
    ├── se8350_controller.py
    └── README.md
```

## Prerequisites

- Docker
- Docker Compose

## Running the Simulation

1. Clone this repository
2. Navigate to the project root directory
3. Run `docker-compose up --build`

The SE8350 Room Controller simulation will start and be accessible via BACnet/IP on port 47808.

## Updating the Project

To update or extend the project, modify the `se8350_controller.py` file in the `se8350_controller` directory. Ensure to update the `README.md` files and `requirements.txt` if new dependencies are added.

---

<!--- PROMPT_START -->

AI Assistant Instructions:

1. When updating this file, maintain the current structure and style.
2. If adding new sections, place them before the "Updating the Project" section.
3. Keep the project description concise and focused on the main features.
4. Ensure the "Prerequisites" and "Running the Simulation" sections remain clear and easy to follow.
5. Update the "Project Structure" if new files or directories are added.
6. Do not remove or modify this prompt section.
<!--- PROMPT_END -->
