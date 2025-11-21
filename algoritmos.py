def procura_DFS(self, start, finish, path=[], visited=set()):
        visited.add(start)
        path.append(start)

        if start == finish:
            cost = self.calcula_custo(path)
            return path, cost
        
        for node, _ in self.getNeighbours(start):
            if node not in visited:
                ans = self.procura_DFS(node, finish, path=path, visited=visited)
                
                if ans is not None:
                  return ans
        
        path.pop()
        return None

def procura_BFS(self, start, finish, path=[], visited=set()):
        q = []
        q.append(start)

        visited.add(start)
        origin = ()
        origin(start) = start

        while len(q) > 0:
            cur_node = q[0]
            q = q[1:]

            if cur_node == finish:
                break

            for node, _ in self.getNeighbours(cur_node):
                if node not in visited:
                    visited(node)
                    q.append(node)
                    origin(node) = cur_node
        
        if origin.get(finish) is None:
            return None
        
        path_cur_node = origin(finish)

        while True:
            if path_cur_node == origin.get(path_cur_node):
                break
            
            path.insert(0, path_cur_node)
            path_cur_node = origin.get(path_cur_node)
        
        path_cost = self.calcula_custo(path)
        return path, path_cost