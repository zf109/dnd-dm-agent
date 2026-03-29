import { useState, useEffect, useCallback } from 'react';

interface CampaignInstance {
  name: string;
  display_name: string;
  character: string;
  character_file: string;
  beat: string;
}

interface Character {
  name: string;
  display_name: string;
}

interface Template {
  name: string;
  display_name: string;
  characters: Character[];
}

interface Props {
  onStart: (campaign: string, character: string, isResume: boolean) => void;
}

export function CampaignBrowser({ onStart }: Props) {
  const [instances, setInstances] = useState<CampaignInstance[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [selectedCharacter, setSelectedCharacter] = useState('');
  const [creating, setCreating] = useState(false);

  const refresh = useCallback(() => {
    setLoading(true);
    Promise.all([
      fetch('/api/campaigns').then((r) => r.json()),
      fetch('/api/templates').then((r) => r.json()),
    ])
      .then(([campaigns, templateData]) => {
        setInstances(campaigns.instances ?? []);
        setTemplates(templateData.templates ?? []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  // Reset character when template changes
  useEffect(() => { setSelectedCharacter(''); }, [selectedTemplate]);

  const activeTemplate = templates.find((t) => t.name === selectedTemplate);

  const handleDelete = async (name: string) => {
    await fetch(`/api/campaigns/${name}`, { method: 'DELETE' });
    setConfirmDelete(null);
    refresh();
  };

  const handleCreate = async () => {
    if (!selectedTemplate || !selectedCharacter || creating) return;
    setCreating(true);
    try {
      const resp = await fetch('/api/campaigns', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ template: selectedTemplate, character: selectedCharacter }),
      });
      if (!resp.ok) return;
      const data = await resp.json();
      onStart(data.instance, data.character, false);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="browser-overlay">
      <div className="browser">

        <div className="browser-header">
          <h1 className="browser-title">⚔ D&amp;D DM Agent</h1>
          <p className="browser-subtitle">Choose an adventure or begin a new one</p>
        </div>

        <div className="section-label">Adventures in Progress</div>

        {loading ? (
          <div className="browser-skeleton">
            <div className="skeleton-row" />
            <div className="skeleton-row" />
          </div>
        ) : instances.length === 0 ? (
          <div className="empty-state">No adventures in progress</div>
        ) : (
          <div className="campaign-list">
            {instances.map((inst) => (
              <div
                key={inst.name}
                className={`campaign-row${confirmDelete === inst.name ? ' confirming' : ''}`}
              >
                <div className="campaign-info">
                  <div className="campaign-name">{inst.display_name}</div>
                  <div className="campaign-meta">
                    {inst.character}
                    {inst.beat && <><span className="sep">·</span><span className="beat">{inst.beat}</span></>}
                  </div>
                </div>

                {confirmDelete === inst.name ? (
                  <div className="confirm-prompt">
                    Delete this adventure?
                    <button className="btn-confirm-yes" onClick={() => handleDelete(inst.name)}>Yes</button>
                    <button className="btn-confirm-cancel" onClick={() => setConfirmDelete(null)}>Cancel</button>
                  </div>
                ) : (
                  <div className="campaign-actions">
                    <button
                      className="btn-resume"
                      onClick={() => onStart(inst.name, inst.character_file, true)}
                    >
                      Resume
                    </button>
                    <button className="btn-delete" onClick={() => setConfirmDelete(inst.name)}>✕</button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        <div className="browser-divider" />

        <div className="section-label">Start New Adventure</div>

        <div className="new-campaign">
          <div className="form-row">
            <select
              className="form-select"
              value={selectedTemplate}
              onChange={(e) => setSelectedTemplate(e.target.value)}
            >
              <option value="">— Select a campaign —</option>
              {templates.map((t) => (
                <option key={t.name} value={t.name}>{t.display_name}</option>
              ))}
            </select>
            <select
              className="form-select"
              value={selectedCharacter}
              onChange={(e) => setSelectedCharacter(e.target.value)}
              disabled={!selectedTemplate}
            >
              <option value="">— Select a character —</option>
              {(activeTemplate?.characters ?? []).map((c) => (
                <option key={c.name} value={c.name}>{c.display_name}</option>
              ))}
            </select>
          </div>
          <button
            className="btn-start"
            disabled={!selectedTemplate || !selectedCharacter || creating}
            onClick={handleCreate}
          >
            {creating ? 'Starting\u2026' : 'Start New Adventure'}
          </button>
        </div>

      </div>
    </div>
  );
}
