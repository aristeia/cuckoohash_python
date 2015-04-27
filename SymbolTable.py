"""

// This abstract class defines a symbol table, such as a hash table. It 
// is pretty close to being an interface, save for a couple of simple methods 
// near the end.

abstract class SymbolTable<K,V> {
    // map key to value
    abstract public void put(K key, V value);

    // return key's value
    abstract public V get(K key);

    // remove key-value pair
    abstract public void delete(K key);	

    // how many pairs?
    abstract public int size();	

    // get *all* the keys
    //abstract public Iterable<K> keys();	

    // is key present?
    public boolean contains(K key) { return (get(key) != null); }

    // is table empty?
    public boolean isEmpty() { return (size()==0); }	
}"""

class SymbolTable:
    def put(self,key,value):
        pass

    def get(self,key):
        pass

    def delete(self,key):
        pass

    def size(self):
        pass

    def keys(self):
        pass

    def contains(key):
        return (get(key) is not null)

    def isEmpty(self):
        return (size(self)==0)
