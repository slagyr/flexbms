# Hardware Tests

1) Batt+/- Continuity.  
    - Using a multimeter in continuity mode, place read lead on BATT+, black on BATT-.  
        - Verify NO continuity.
    - Reverse leads, red on BATT-, blank on BATT+
        - Verify continuity with ~700 ohms (protection diodes have reverse resistance)
    - Defective parts may cause a short circuit.
    - Perform this test BEFORE connecting the battery.

2) Cell Connections
    - Connect the cell leads
    - Connect the micro-controller
    - Press the BOOT button the BQ board
    - Power the micro-controller
    - Verify voltage readings on voltage screen
        - New cells should all be at ~3.6V
    - Manual verification:
      - Using multimeter, place black lead on C0
      - Place red lead on C1, verify 3.6V
      - Move red lead to C2, verify 7.2V, etc..
    
3) Charge/Discharge FETs
    - Using multimeter measuring resistance (~2k ohms)
    - Red lead on BATT+, black lead in PACK+
    - Disable both FETs (manipulating hard via MicroPython REPL is handy)
        - Verify NO continuity (0L/Infinite resistance)
    - Enable Discharge FET
        - Verify continuity with ~200 ohms
    - Enable Charge FET
        - Verify 0 ohms

        
        