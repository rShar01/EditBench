
import React, { useEffect, useState, useCallback } from 'react';
import styles from './GameUI.module.css';
import { useLocation } from 'react-router-dom';
import CharacterStatUI from '../character-stat-ui/CharacterStatUI';
import Sprite from '../sprite/Sprite';
import GameMap from '../game-map/GameMap';
import { characterData } from '../character-data/CharacterData';
import MapCharacter from '../map-character/MapCharacter';

const publicFolder = `${process.env.PUBLIC_URL}`;

const GameUI = () => {
  const location = useLocation();
  const frontPageState = location.state || {};
  const character = frontPageState.character; 
  const map = frontPageState.map;
  // UPDATE UI STATES

  // Default UI states
  const [characterUIState, setCharacterUIState] = useState({}); 
  const [mapState, setMapState] = useState({});
  const [clickedState, setClickedState] = useState(null);
  const [selectedCharacter, setSelectedCharacter] = useState("Alfonse");

  const characterNames = ["Alfonse", "Sharena", "Anna", "Fjorm"];

  const [characters, setCharacters] = useState(
    characterNames.map(characterName => characterData(characterName))
  );

  const mapSetup = useCallback(() => {
    if (!map) {
      return {}; 
    }

    const name = map.name || '';
    const imageUrl = map.image ? `${publicFolder}${map.image}` : `${process.env.PUBLIC_URL}/assets/images/map/Map_S0001.jpg`;
    return { name, imageUrl };
  }, [map]);

  useEffect(() => {
    setMapState(mapSetup());
  }, [map, mapSetup]); 
  useEffect(() => {
    if (selectedCharacter) { 
      const selectedCharData = characterData(selectedCharacter);

      setCharacterUIState({
        charName : selectedCharacter,
        level : selectedCharData.level,
        wpn : selectedCharData.wpn,
        hp : selectedCharData.hp,
        atk : selectedCharData.atk,
        spd : selectedCharData.spd,
        def : selectedCharData.def,
        res : selectedCharData.res
      });
    }
  }, [selectedCharacter, setCharacterUIState]);

  // Update UI State after click
  const handleGridClick = useCallback((gridX, gridY) => {
    console.log(`Grid clicked at X: ${gridX}, Y: ${gridY}`);
    setClickedState({ gridX, gridY });
  }, [setClickedState, clickedState]);

  return (
    <div className={styles['game-container']}>
      <div className={styles['content-wrapper']}>
        <CharacterStatUI
          charName={characterUIState.charName || ''} 
          level={characterUIState.level || 0}
          wpn={characterUIState.wpn || ''}
          hp={characterUIState.hp || 0}
          atk={characterUIState.atk || 0}
          spd={characterUIState.spd || 0}
          def={characterUIState.def || 0}
          res={characterUIState.res || 0}
        />
        <div className={styles['map-container']}>
          <GameMap
            onGridClick={handleGridClick}
          />
        </div>
        {characterNames.map((characterName) => (
          <MapCharacter
            key={characterName}
            character={characterName}
          />
        ))}
        <div className={styles['actionButtonsContainer']}>
          <div className={styles['button-group']}>
            <div className={styles['leftAlignedButtons']}>
              <Sprite spriteName="ButtonBg1">
                <button className={styles['action-button']}>1</button>
              </Sprite>
              <Sprite spriteName="ButtonBg1">
                <button className={styles['action-button']}>2</button>
              </Sprite>
              <Sprite spriteName="ButtonBg1">
                <button className={styles['action-button']}>3</button>
              </Sprite>
            </div>
            <div className={styles['rightAlignedButtons']}>
              <Sprite spriteName="ButtonBg1">
                <button className={styles['action-button']}>4</button>
              </Sprite>
              <Sprite spriteName="ButtonBg1">
                <button className={styles['action-button']}>5</button>
              </Sprite>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GameUI;
