# mdp-algo
- 28/09/18: Uploaded code for clearing checklist.<br/>
- 01/10/18: 
          Reuploaded code. Input adapted for hexstring
          Uploaded week 8 code (non-integrated)
          <br/>
- 04/10/18:
          Updated week 8 code (integrated)
- 08/10/18:
          Updated week 8 code for image recognition<br/>
          Bug fixes for 0 crash states(TBC)<br/>
          Further adapted code for Android killswitch<br/>
- 11/10/18:
          version 17 is week8-ready.<br/>         
          
          1. Note: Non-week uploads are not to be used for actual run.
          2. Requires IDLE and wampserver to run.
            2a. Put the HTML + js file into the 'www' folder of your wampserver directory to run
            2b. Change the last line in the Python code to suit the folder to open the HTML file from.
          3. Sample arena simulation input:
             Arena1:Empty
              C000000000000000000000000000000000000000000000000000000000000000000000000003
             Arena2:
             C0E000000000000001001E1000200040000800F0000000030006000C7E000400000000000203
             Arena3:
             C0000000010000000072000000000001C00000002000000007E00001C0000000008000000003
             Arena4:
             C0000000002000401080E10000000000000000430000000000000087E1000200000000000103
             Arena5:
             C00000000008010002000400001C000000000000001F803F0000000040000040000008000003
             Arena6:
             C0100020004000000000000FC1000000000000004001004000000000E0000000020004000803
             Arena7:
             C1000002000000807000008001000200040808101020004000800100000E0100000040000083
             Arena8:
             C00000000030006010C0E180000000000000004300000000000000FFE1000200000000000103
          4. To run realtimemap:
             Put index.html, testsocket.py, the jquery file, and the MDP code to the directory for running the server.
             
##### To do:
- [X] Change simulation input to hex
- [X] Adapt code for week 8 run
- [X] Begin working on integration (With RPI) (Using ~~multiprocess~~ socket)
- [X] Adapt code for burst mode
- [X] Adapt code for Android (start explore, start fastest)
- [X] Adapt code for image recognition
- [ ] Improve step evaluation to include turning as 1 step
- [ ] Improve code for image recognition
- [ ] Find a way to activate killswitch without affecting the code

