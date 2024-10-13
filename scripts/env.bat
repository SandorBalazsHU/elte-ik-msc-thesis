cd C:\DATA\kutmod
python -m venv venv
venv\Scripts\activate
pip install numpy
pip install torch==2.1.1+cu121 -f https://download.pytorch.org/whl/torch_stable.html
pip install torchvision
pip install torchsummary
pip install pandas
pip install jupyter
pip install graphviz
pip install matplotlib
pip install IPython
pip install sklearn
pip install seaborn
pip install pretty_confusion_matrix

jupyter notebook