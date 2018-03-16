How to run api to create holes
Note:
*When import other models other than "bigbunny.obj", please change the value of variable "size_x" in codes.
*There are some bugs in meshmixer "difference" operation, so sometimes the script might fail.

*****Step by step generation*******
1. open meshmixer and import "bigbunny.obj"(in this folder)
2. python blowhole_generation_step.py.
3. go back to meshmixer.
4. select a area then click "Add Position" button.
5. holes with suitable size will be generated. if no suitable size found, will return error message on GUI.
6. repeat step 4 to create hole at other areas.

*****One time generation*******
1. open meshmixer and import "bigbunny.obj"(in this folder)
2. python blowhole_generation_DFS.py.
3. go back to meshmixer.
4. select a area then click "Add Position" button, the position will be stored in system.
5. repeat step 4 to select other areas.
6. click "blow hole!" button to generate the model automatically, the algorithm is based on depth first search backtracking. If no solution is found, the GUI will display error message.

*****Create holes with annotation step by step******
1. open meshmixer and import "bigbunny.obj"(in this folder)
2. python blowhole_generation_func.py.
3. go back to meshmixer.
4. select a area then click "Add Position" button.
5. holes with suitable size will be generated. if no suitable size found, will return error message on GUI.
6. After the hole is created, type the function for this hole in the dialog, like "www.facebook.com" and "batman.mov". This will save a pickle dictionary named "function_dict.p" in this folder. It looks like {6:"www.facebook.com",8:"batman.move"}, where 6 and 8 are the size of sphere.
7. repeat step 4 to create hole at other areas.

*****Create holes with annotation one time******
1. open meshmixer and import "bigbunny.obj"(in this folder)
2. python blowhole_generation_func_dfs.py.
3. go back to meshmixer.
4. select a area then click "Add Position" button.
5. A ring will be created at that position to remind users where they selected. Then user type the function for this hole in the dialog, like "www.facebook.com" and "batman.mov".
6. repeat step 4 to create hole at other areas.
7. click "blow hole!" button to generate the model automatically, the algorithm is based on depth first search backtracking. If no solution is found, the GUI will display error message. This step also save a pickle dictionary named "action_dict.p" in this folder. It looks like {6:"www.facebook.com",8:"batman.move"}, where 6 and 8 are the size of sphere.