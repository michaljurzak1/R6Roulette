'use client';

import { useState, useEffect } from 'react';
import './globals.css';
import defenders from '../public/defenders.json';
import attackers from '../public/attackers.json';

interface OperatorsResponse {
  operator_names: string[];
  operator_icons: string[];
}

const OperatorsComponent = ({ bannedOperators }: { bannedOperators: { a: string[], d: string[] } }) => {
  const [bannedOperatorsInfo, setBannedOperatorsInfo] = useState<string[]>([]);

  useEffect(() => {
    // Combine both arrays into one and set the state
    const combinedBannedOperators = [...bannedOperators.a, ...bannedOperators.d];
    setBannedOperatorsInfo(combinedBannedOperators);
  }, [bannedOperators]);

  return (
    <div className="banned-info">
      Banned operators: {bannedOperatorsInfo.length > 0 ? bannedOperatorsInfo.join(', ') : 'None'}
      <style jsx>{`
        .banned-info {
          color: #ff8c73;
          font-size: 1.2rem;
          margin-bottom: 20px;
        }
      `}</style>
    </div>
  );
};

const getAllOperatorsBySide = (side: 'a' | 'd', bans: string[]): OperatorsResponse => {
  const operator_names: string[] = [];
  const operator_icons: string[] = [];

  if (side === 'a') {
    attackers.attackers.forEach((operator: any) => {
      const name = operator.name;
      const icon = operator.icon;
      if (!bans.includes(name)) {
        operator_names.push(name);
        operator_icons.push(icon);
      }
    });
  } else if (side === 'd') {
    defenders.defenders.forEach((operator: any) => {
      const name = operator.name;
      const icon = operator.icon;
      if (!bans.includes(name)) {
        operator_names.push(name);
        operator_icons.push(icon);
      }
    });
  }

  return { operator_names, operator_icons };
};

const getRandomOperatorsBySide = (
  side: 'a' | 'd',
  numOperators: number,
  attackerBans: string[],
  defenderBans: string[]
): OperatorsResponse => {
  const operator_names: string[] = [];
  const operator_icons: string[] = [];
  const availableOperators: { name: string; icon: string }[] = [];

  if (side === 'a') {
    attackers.attackers.forEach((operator: any) => {
      if (!attackerBans.includes(operator.name)) {
        availableOperators.push({ name: operator.name, icon: operator.icon });
      }
    });
  } else if (side === 'd') {
    defenders.defenders.forEach((operator: any) => {
      if (!defenderBans.includes(operator.name)) {
        availableOperators.push({ name: operator.name, icon: operator.icon });
      }
    });
  }

  while (operator_names.length < numOperators && availableOperators.length > 0) {
    const randomIndex = Math.floor(Math.random() * availableOperators.length);
    const selectedOperator = availableOperators.splice(randomIndex, 1)[0];
    operator_names.push(selectedOperator.name);
    operator_icons.push(selectedOperator.icon);
  }

  return { operator_names, operator_icons };
};

export default function Roulette() {
  const [side, setSide] = useState<'a' | 'd'>('a'); // 'a' for attackers, 'd' for defenders
  const [count, setCount] = useState(1);
  const [operators, setOperators] = useState<OperatorsResponse>({ operator_names: [], operator_icons: [] });
  const [bannedOperators, setBannedOperators] = useState<{ a: string[], d: string[] }>({ a: [], d: [] });
  const [randomOperators, setRandomOperators] = useState<OperatorsResponse>({ operator_names: [], operator_icons: [] });
  const [search, setSearch] = useState('');
  const currentColor = side === 'a' ? '#0595fc' : '#fc8105';
  
  useEffect(() => {
    fetchOperators();
  }, [side]);

  const fetchOperators = async () => {
    try {
      // const response = await axios.get<OperatorsResponse>(`http://127.0.0.1:8000/operators?side=${side}`);
      const response = getAllOperatorsBySide(side, bannedOperators[side]);
      setOperators(response);
      // setOperators(response.data);
    } catch (error) {
      console.error('Error fetching operators:', error);
    }
  };

  const handleOperatorClick = (operator: string) => {
    if (bannedOperators[side].includes(operator)) {
      setBannedOperators({
        ...bannedOperators,
        [side]: bannedOperators[side].filter(op => op !== operator)
      });
    } else if (bannedOperators[side].length < 2) {
      setBannedOperators({
        ...bannedOperators,
        [side]: [...bannedOperators[side], operator]
      });
    }
  };
  
  const handleSideChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newSide = e.target.checked ? 'd' : 'a';
    setSide(newSide);
    setBannedOperators({ a: [], d: [] });
  };

  const fetchRandomOperators = async () => {
    const response = getRandomOperatorsBySide(side, count, bannedOperators.a, bannedOperators.d);
    console.log(response);
    setRandomOperators(response);
  };
  
  const filteredOperators = operators.operator_names
    .map((name, index) => ({ name, icon: operators.operator_icons[index] }))
    .filter(({ name }) => name.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="container">
      <h1>R6Roulette</h1>
      <div className="controls">
        <label>
          Count:{" "}
          <input
            type="range"
            min="1"
            max="5"
            value={count}
            onChange={(e) => setCount(parseInt(e.target.value))}
          />
          &nbsp;{count}
        </label>
        <div className="switchContainer">
          <div className="left-side">Attackers</div>
          <label className="switch" htmlFor="checkbox">
            <input type="checkbox" id="checkbox" onChange={handleSideChange}/>
            <div className="slider round"></div>
          </label>
          <div className="right-side">Defenders</div>
        </div>
        <button className="roulette-button" 
        onClick={fetchRandomOperators} 
        style={{backgroundColor: currentColor}}>
          Spin Roulette
        </button>
      </div>
      <div className="random-operators">
        {randomOperators.operator_names.map((operator, index) => (
          <div key={operator} className="operator random-operator" style={{ outline: `2px solid ${currentColor}` }}>
            <img src={randomOperators.operator_icons[index]} alt={operator} />
            {operator}
          </div>
        ))}
      </div>
      <input
        type="text"
        placeholder="Search operators..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="search-bar"
      />
      
      <OperatorsComponent bannedOperators={bannedOperators}/>
      
      <div className="operators">
        {filteredOperators.map(({ name, icon }) => (
          <div
            key={name}
            className={`operator ${bannedOperators[side].includes(name) ? 'banned' : ''}`}
            onClick={() => handleOperatorClick(name)}
            style={{
              pointerEvents: bannedOperators[side].length < 2 || bannedOperators[side].includes(name) ? 'auto' : 'none',
              cursor: bannedOperators[side].length < 2 || bannedOperators[side].includes(name) ? 'pointer' : 'default',
            }}
          >
            <img src={icon} alt={name} />
            <div className="operator-name">{name}</div>
          </div>
        ))}
      </div>
      <style jsx>{`
        h1 {
          padding: 10px;
          font-size: 3rem;
          font-weight: 700;
          font-style: italic;
        }
        
        .container {
          background-color: #121212;
          color: #ffffff;
          display: flex;
          flex-wrap: wrap;
          flex-direction: column;
          align-items: center;
          margin: 0;
          padding: 0;
          width: 100%;
          max-width: 100vw;
          box-sizing: border-box;
          justify-content: center;
          text-align: left; 
        }
        .switchContainer {
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 20px;
        }  
        
        .left-side, .right-side {
          flex: 1;
          text-align: center;
          margin: 0 10px;
        }
        .controls {
          font-size: 1.15rem;
          margin-bottom: 20px;
          display: flex;
          flex-direction: column;
          align-items: center;
        }
        .switch {
          display: inline-block;
          height: 34px;
          position: relative;
          width: 60px;
        }

        .switch input {
          display:none;
        }

        .slider {
          background-color: #0595fc;
          bottom: 0;
          cursor: pointer;
          left: 0;
          position: absolute;
          right: 0;
          top: 0;
          transition: .4s;
        }

        .slider:before {
          background-color: #fff;
          bottom: 4px;
          content: "";
          height: 26px;
          left: 4px;
          position: absolute;
          transition: .4s;
          width: 26px;
        }

        input:checked + .slider {
          background-color: #fc8105;
        }

        input:checked + .slider:before {
          transform: translateX(26px);
        }

        .slider.round {
          border-radius: 34px;
        }

        .slider.round:before {
          border-radius: 50%;
        }
        
        .roulette-button {
          background-color: #44db1f;
          color: #ffffff;
          border: none;
          padding: 10px 20px;
          cursor: pointer;
          font-size: 1.2rem;
          margin-top: 10px;
          border-radius: 10px;
        }
        .random-operators {
          display: flex;
          flex-wrap: wrap;
          gap: 30px;
          justify-content: center;
          margin: 20px;
        }
        .operators {
          display: flex;
          flex-wrap: wrap;
          align-items: center;
          gap: 1vw;
          width: 100%; 
          max-width: 85vw;
          justify-content: center;
        }
        .operator {
          flex: 0 0 auto;
          padding: 10px;
          background-color: #333;
          border-radius: 5px;
          transition: background-color 0.3s;
          text-align: center;
          width: 100px;
        }
        .operator:hover {
          background-color: #555;
        }
        .operator.banned {
          background-color: #222;
          outline: 2px solid #555
        }
        .operator.banned:hover {
          background-color: #444;
        }
        .operator img {
          width: 50px;
          height: 50px;
          display: block;
          margin: 0 auto 5px;
        }
        .operator-name {
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .search-bar {
          margin: 20px;
          padding: 10px;
          width: 100%;
          max-width: 300px;
          border-radius: 5px;
          border: none;
          background-color: #333;
          color: #ffffff;
        }
        .search-bar::placeholder {
          color: #bbbbbb;
        }
        .random-operator {
          transform: scale(1.2);
          outline: 2px solid #44db1f;
        }
        .random-operator:hover {
          background-color: #333;
        }
        .banned-info {
          color: #111;
          font-size: 1.2rem;
        }
      `}</style>
    </div>
  );
}
