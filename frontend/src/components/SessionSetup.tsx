import { useState, useEffect } from 'react';

interface Props {
  onStart: (campaign: string, character: string) => void;
}

export function SessionSetup({ onStart }: Props) {
  const [campaigns, setCampaigns] = useState<string[]>([]);
  const [characters, setCharacters] = useState<string[]>([]);
  const [selectedCampaign, setSelectedCampaign] = useState('');
  const [selectedCharacter, setSelectedCharacter] = useState('');
  const [loading, setLoading] = useState(true);
  const [charsLoading, setCharsLoading] = useState(false);

  useEffect(() => {
    fetch('/api/campaigns')
      .then((r) => r.json())
      .then((data) => {
        setCampaigns(data.instances ?? []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selectedCampaign) {
      setCharacters([]);
      setSelectedCharacter('');
      return;
    }
    setCharsLoading(true);
    fetch(`/api/campaigns/${selectedCampaign}/characters`)
      .then((r) => r.json())
      .then((data) => {
        setCharacters(data.characters ?? []);
        setSelectedCharacter('');
        setCharsLoading(false);
      })
      .catch(() => setCharsLoading(false));
  }, [selectedCampaign]);

  const canStart = selectedCampaign && selectedCharacter;

  return (
    <div className="setup-overlay">
      <div className="setup-card">
        <div className="setup-header">
          <h1 className="setup-title">⚔ D&D DM Agent</h1>
          <p className="setup-subtitle">Choose your campaign and character to begin</p>
        </div>

        <div className="setup-fields">
          <div className="setup-field">
            <label className="setup-label">Campaign</label>
            {loading ? (
              <div className="setup-loading">Loading campaigns...</div>
            ) : campaigns.length === 0 ? (
              <div className="setup-empty">No campaigns found. Create one first.</div>
            ) : (
              <select
                className="setup-select"
                value={selectedCampaign}
                onChange={(e) => setSelectedCampaign(e.target.value)}
              >
                <option value="">— Select a campaign —</option>
                {campaigns.map((c) => (
                  <option key={c} value={c}>
                    {c.replace(/_/g, ' ')}
                  </option>
                ))}
              </select>
            )}
          </div>

          <div className="setup-field">
            <label className="setup-label">Character</label>
            {charsLoading ? (
              <div className="setup-loading">Loading characters...</div>
            ) : !selectedCampaign ? (
              <div className="setup-empty">Select a campaign first</div>
            ) : characters.length === 0 ? (
              <div className="setup-empty">No characters in this campaign</div>
            ) : (
              <select
                className="setup-select"
                value={selectedCharacter}
                onChange={(e) => setSelectedCharacter(e.target.value)}
              >
                <option value="">— Select a character —</option>
                {characters.map((c) => (
                  <option key={c} value={c}>
                    {c.replace(/_/g, ' ')}
                  </option>
                ))}
              </select>
            )}
          </div>
        </div>

        <button
          className="setup-start-btn"
          disabled={!canStart}
          onClick={() => onStart(selectedCampaign, selectedCharacter)}
        >
          Begin Adventure
        </button>
      </div>
    </div>
  );
}
