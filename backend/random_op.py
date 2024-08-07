import sys, argparse
from random import randint

return_ops = []

def rand(kwargs, attackers=None, defenders=None):
    
    #attackers, defenders = _attackers.copy(), _defenders.copy()
    return_ops = []
    for key, value in kwargs:
        try:
            if key == 'defenderbans' and value is not None and defenders is not None:
                for o in value:
                    defenders.remove(o)
            elif key == 'attackerbans' and value is not None and attackers is not None:
                for o in value:
                    attackers.remove(o)
            elif key == 'defenders' and value is not None and defenders is not None:
                if value > len(defenders):
                    value = len(defenders)
                elif value <= 0:
                    value = 1
                    
                side = defenders
                if value is not None:
                    for _ in range(value):
                        rand_o = side[randint(0, len(side)-1)]
                        return_ops.append(rand_o)
                        side.remove(rand_o)
                        
            elif key == 'attackers' and value is not None and attackers is not None:
                if value > len(attackers):
                    value = len(attackers)
                elif value <= 0:
                    value = 1
                
                side = attackers
                if value is not None:
                    for _ in range(value):
                        rand_o = side[randint(0, len(side)-1)]
                        return_ops.append(rand_o)
                        side.remove(rand_o)
        
        except Exception as e:
            print(e)
            raise SyntaxError("Invalid input")
        
    return return_ops
            
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-ab', '--attackerbans', help='list of banned attacker operators', nargs=2)
    parser.add_argument('-db', '--defenderbans', help='list of banned defender operators', nargs=2)
    parser.add_argument('-d', '--defenders', type=int, help='number of defenders to randomly select')
    parser.add_argument('-a', '--attackers', type=int, help='number of attackers to randomly select')
    args = parser.parse_args(sys.argv[1:])

    print(args._get_kwargs())
    print(rand(args._get_kwargs()))