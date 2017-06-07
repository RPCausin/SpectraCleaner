# SpectraCleaner
Use this program to navigate through your files and visualize the selected OPUS spectrum. You can remove the selected spectrum by pressing the `Del` key of your keyboard.

## INSTALLATION INSTRUCTIONS

1. Uncompress this folder.

2. Write the following command on the command line:
```python3 setup.py install --user```

3. By entering `SpectraCleaner` in the command prompt, the app should run. The executable file appears in the folder `~/.local/bin`. If you have problems, you can go there (`cd ~/.local/bin`) and then execute the file (`./SpectraCleaner`).

--------------------------------------------------------------------------------

Note that you should have Python3 installed and added to your system's path in 
order that step 2 works.

If some package is not automatically installed when running `python3 setup.py 
install --user`, you can install all the required packages like this:
```pip3 install AnyQt opusFC pyqtgraph```
And then go back to step 2.
(Write `sudo` at the beginning if you need root permissions)

You can install pip3 with (Ubuntu): `sudo apt-get install python3-pip`

--------------------------------------------------------------------------------

For any questions or suggestions contact rpcausin@gmail.com.
