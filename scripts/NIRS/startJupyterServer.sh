#!/bin/bash

# usage: bash startJupyterServer.sh <port number>

if [ -z "$1" ]; then
	echo "No argument supplied."
	echo "Usage: bash startJupyterServer.sh <port number>"
fi

if [[ $1 -ge 10000 ]] | [[ $1 -le 8999 ]]; then
	echo "You used port number $1."
	echo "Use a port number between 9000 and 9999 please."
fi


source /data/perlman/moochie/resources/server_access/NIRSenv/bin/activate

user=$(whoami)

python3 -m ipykernel install --user --name=NIRSenv

if ! tmux new-session -d -s jupyter-server-$1; then 
	
	echo "Failed to start jupyter server."
	echo "You likely already have a jupyter server running. You can attach it to view the server info with 'tmux attach -t jupyter-server'."
        echo "or delete with 'tmux kill-session -t jupyter-server'"
	exit 1

fi

if ! tmux send -t jupyter-server "jupyter lab --port=$1 --no-browser" ENTER; then

	echo "Failed to start the jupyter server. Make sure you're not already running a server, and that the port you're submitting isn't already in use by you or another user."
	echo "Check currently-running tmux sessions with: "
        echo "tmux ls"
	echo ""
	echo "To kill one of the tmux session, run:"
	echo "tmux kill-session -t jupyter-server"
	exit 1

fi

sleep 5s

if [[ $(jupyter notebook list | grep ::) ]]; then

	echo $(jupyter notebook list)

	echo "Tmux session started on port $1."
	echo ""
	echo "From your local machine, run the following command (while on VPN or WUSTL internet) to connect to the server:"
	echo "ssh -N -f -L 8888:localhost:$1 $user@dynosparky.neuroimage.wustl.edu" 
	echo ""
	echo "and then open a web browser and go to the address, 'localhost:8888'"
	echo ""
	echo "If you are connecting from a new computer, you will need to copy the access token from the URL listed above."
	echo "Copy the string of the https://localhost...... address following 'token=' ."
	echo "This is what you will paste in the 'password' entry when connecting."

else

	echo "There are no sessions listed in 'jupyter notebook list'"
	echo "Something may have gone wrong."
	exit 1

fi
