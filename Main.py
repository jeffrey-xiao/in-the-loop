import indicoio
from newspaper import Article 

indicoio.config.api_key = '4d5aca20b4ea5a85a667de57c23d2e50'

filein = open("in.txt", "r")
fileout = open("out.txt", "w")


for line in filein:
    article = Article(line)
    article.download()
    article.parse()
    text = article.text.encode('ascii', 'ignore').decode('ascii')
    fileout.write(text + "\n")