from qdrant import QDrantVectorDatabase

vector = QDrantVectorDatabase()
vector.add_task('Ютуб крутой')
print(vector.get_task('ютуб'))