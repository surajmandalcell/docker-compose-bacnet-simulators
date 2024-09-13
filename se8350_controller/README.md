# SE8350 Room Controller Module

This module simulates a Schneider Electric SE8350 Room Controller using the BACnet/IP protocol.

## Files

- `Dockerfile`: Defines the Docker image for the SE8350 controller simulation.
- `se8350_controller.py`: Contains the main simulation logic for the SE8350 controller.

## Features

- Room temperature monitoring
- Temperature setpoint
- Humidity monitoring
- Occupancy status
- Fan status (Off, Low, High)
- HVAC mode (Off, Auto, Heat, Cool, Emergency Heat)

## Customization

To modify the behavior of the SE8350 controller, edit the `se8350_controller.py` file. You can adjust the update frequency, add new BACnet objects, or modify the simulation logic as needed.

---

<!--- PROMPT_START -->

AI Assistant Instructions:

1. When updating this file, maintain the current structure and style.
2. Keep the module description and features list up-to-date with any changes made to the `se8350_controller.py` file.
3. If adding new files to this module, list them in the "Files" section with a brief description.
4. Ensure the "Customization" section remains relevant and helpful for users who want to modify the simulation.
5. Do not remove or modify this prompt section.
<!--- PROMPT_END -->
