# Frontend Manual - Browser Endpoint explanation

 # Launching the frontend

 - Just open the `index.html` file in your browser (double-click).

 # HTML - index.html

 1. There is showed first an instructions menu:
     - It appears when loading the website. Closes by pressing the `Got it! - Begin` button. 
     - The menu covers the screen where the keypad is being placed, so the `Start Session` button to begin the recording is only possible if the instructions modal is closed.
  2. Aferwards it is displayed the web User Interface.

 ---

 # CSS - Styles.css 
 Models the index UI appearance.
 The `#keypad` arranges the 4 vital cells in a row.
 The `.key` assigns the size of the cells (8x8cm), apart from other functions like establishing the separation gap between cells.
 The commands `.key.on` and `.key.off` modulate the flickering appearance of the cells between on-off transitions. 
 The `.key.selected` displays a green color if the cell was correctly chosen. 
 Everything related to `#modal` builds the appearance of the initial instructions menu.
 The `#...-panel` refers to the changes linked to the **Start Session button**.

---

 # **JS Files**

 # App.js 
 - Frontend is initialised here in order to call other js.
 - This JavaScript will be the entry point regarding the communication pathway (WS) with the frontend.
 - It also calls the flicker engine as well as initialising to start the test or recording.

 # Flicker.js
 - It is based on the flicker engine module following the SSVEP paradigm.
 - Each emoji flickers at its frequency (4 different assigned to each cell) by calling the requestAnimationFrame for temporal accuracy; considering as well the screen refresh rate.
 - The frequencies are read from the `data-freq` attribute taken from the **DOM** (built from the index.html when it is loaded).
 - The period is linked to the ms per half cycle due to the on-off transitions. When the cell is asigned to be turned off it is seen as black and when it is on it is seen as white; due to the frequency of oscillation been short it is seen by the human eye as "cell-blinking".


 # Ui.js
 - Displays User Interface helper functionalities.
 - Contains the functions related with the nodes of the **DOM** created by the browser.
 - **setConnectionStatus**: indicates if the server is connected through a client to the browser. 
 - **clearCellSelection**: removes the green feedback color before each new iteration result and it is seen as usual white color appearance. 
 - **showMessage**: displays in a blue color which is the target cell to gaze at and in green if the objective was selected. 
 - **startCountdown**: shows the seconds remaining for the end of the recroding at each iteration (backwards timer).  
 

 # Websocket.js
 - Enables communication between browser and server.
 - It manages the WebSocket connection and automatic re-attempting connection.
 - It has dependencies with the `ui.js` (`setConnectionStatus`, `clearCellSelection`, `showMessage`, `startCountdown` and `stopCountdown`).
 - Connects through the ws once the DOM is loaded. 
 - **connect**: this function opens the connection between the browser and the server; reattempts it 2s later if it was not done.
 - **handleBlockStarted**: tells the user which cell to gaze at while all of them keep flickering at their frequency of oscillation.
 - **handleBlockResult**: clears the previous selection and marks the cell in green if it was detected. 
 - **handleSessionEnded**: finishes the countdown, clears the selection for the next recording session and shows the accuracy rate in percentage and respect to the total number of processed blocks. 
 - **handleSessionEnded**: restores the UI such that a new session can be selected by pressing the Start Button available again.




