import { useState, useEffect } from "react";

const API_BASE = "http://localhost:8000";

function App() {
  const [gender, setGender] = useState("men");
  const [season, setSeason] = useState("winter");
  const [occasion, setOccasion] = useState("casual");

  const [outfit, setOutfit] = useState(null);
  const [alternatives, setAlternatives] = useState([]);
  const [activeSlot, setActiveSlot] = useState(null);

  // Digital Closet State
  const [savedOutfits, setSavedOutfits] = useState([]);
  const [activeView, setActiveView] = useState("generate"); // "generate" or "closet"

  // Loading States
  const [isGenerating, setIsGenerating] = useState(false);
  const [isLoadingAlternatives, setIsLoadingAlternatives] = useState(false);

  // Outfit Naming
  const [showNameModal, setShowNameModal] = useState(false);
  const [outfitName, setOutfitName] = useState("");
  const [editingOutfitId, setEditingOutfitId] = useState(null);
  const [editingName, setEditingName] = useState("");

  // Interactive Dot Matrix Effect
  useEffect(() => {
    const handleMouseMove = (e) => {
      const x = (e.clientX / window.innerWidth) * 100;
      const y = (e.clientY / window.innerHeight) * 100;
      document.documentElement.style.setProperty('--mouse-x', `${x}%`);
      document.documentElement.style.setProperty('--mouse-y', `${y}%`);
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  useEffect(() => {
    const saved = localStorage.getItem("fashionLabsCloset");
    if (saved) {
      setSavedOutfits(JSON.parse(saved));
    }
  }, []);

  // Save to localStorage whenever savedOutfits changes
  useEffect(() => {
    if (savedOutfits.length > 0) {
      localStorage.setItem("fashionLabsCloset", JSON.stringify(savedOutfits));
    }
  }, [savedOutfits]);

  // -----------------------------
  // Generate outfit
  // -----------------------------
  const generateOutfit = async () => {
    setAlternatives([]);
    setActiveSlot(null);
    setIsGenerating(true);

    try {
      const res = await fetch(`${API_BASE}/generate-outfit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          gender,
          season,
          occasion,
          timestamp: Date.now() // Force new generation each time
        })
      });

      const data = await res.json();
      if (data.outfit) {
        setOutfit(data.outfit);
      } else {
        alert("No outfit could be generated");
      }
    } catch (error) {
      alert("Failed to generate outfit. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  // -----------------------------
  // Get alternatives for a slot
  // -----------------------------
  const getAlternatives = async (slot) => {
    setActiveSlot(slot);
    setIsLoadingAlternatives(true);

    try {
      const res = await fetch(`${API_BASE}/slot-alternatives`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          current_outfit: outfit,
          slot,
          gender,
          season,
          occasion,
          top_k: 5
        })
      });

      const data = await res.json();
      setAlternatives(data.alternatives || []);
    } catch (error) {
      alert("Failed to load alternatives. Please try again.");
    } finally {
      setIsLoadingAlternatives(false);
    }
  };

  // -----------------------------
  // Apply alternative
  // -----------------------------
  const applyAlternative = (item) => {
    setOutfit(prev => ({
      ...prev,
      [activeSlot]: item
    }));
    setAlternatives([]);
    setActiveSlot(null);
  };

  // -----------------------------
  // Save outfit to closet
  // -----------------------------
  const saveToCloset = () => {
    if (!outfit) return;
    setShowNameModal(true);
  };

  const confirmSaveOutfit = () => {
    const defaultName = `Outfit - ${new Date().toLocaleDateString()}`;
    const finalName = outfitName.trim() || defaultName;

    const newOutfit = {
      id: Date.now(),
      name: finalName,
      outfit: outfit,
      context: { gender, season, occasion },
      savedAt: new Date().toISOString()
    };

    setSavedOutfits(prev => [newOutfit, ...prev]);
    setShowNameModal(false);
    setOutfitName("");
  };

  const renameOutfit = (id) => {
    const outfitToRename = savedOutfits.find(o => o.id === id);
    if (outfitToRename) {
      setEditingOutfitId(id);
      setEditingName(outfitToRename.name);
    }
  };

  const confirmRename = () => {
    setSavedOutfits(prev => prev.map(o =>
      o.id === editingOutfitId ? { ...o, name: editingName } : o
    ));
    setEditingOutfitId(null);
    setEditingName("");
  };

  // -----------------------------
  // Delete outfit from closet
  // -----------------------------
  const deleteFromCloset = (id) => {
    setSavedOutfits(prev => prev.filter(item => item.id !== id));
    localStorage.setItem("fashionLabsCloset", JSON.stringify(savedOutfits.filter(item => item.id !== id)));
  };

  return (
    <>
      {/* Header */}
      <div className="app-header">
        <div className="header-content">
          <h1
            className="app-title"
            onClick={() => setActiveView("generate")}
          >
            FASHION LABS
          </h1>
          <nav className="header-nav">

            <span
              className={`nav-link ${activeView === "closet" ? "active" : ""}`}
              onClick={() => setActiveView("closet")}
            >
              My Closet ({savedOutfits.length})
            </span>
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="app-container">
        {activeView === "generate" ? (
          <>
            {/* Generate Section */}
            <div className="section-header">
              <h2 className="section-title">Create Your Outfit</h2>
              <p className="section-subtitle">Select your preferences and generate a personalized outfit</p>
            </div>

            {/* Controls */}
            <div className="controls-section">
              <div className="controls-grid">
                <div className="control-group">
                  <label className="control-label">Gender</label>
                  <select value={gender} onChange={e => setGender(e.target.value)}>
                    <option value="men">Men</option>
                    <option value="women">Women</option>
                  </select>
                </div>

                <div className="control-group">
                  <label className="control-label">Season</label>
                  <select value={season} onChange={e => setSeason(e.target.value)}>
                    <option value="winter">Winter</option>
                    <option value="summer">Summer</option>
                  </select>
                </div>

                <div className="control-group">
                  <label className="control-label">Occasion</label>
                  <select value={occasion} onChange={e => setOccasion(e.target.value)}>
                    <option value="casual">Casual</option>
                    <option value="formal">Formal</option>
                  </select>
                </div>
              </div>

              <button
                onClick={generateOutfit}
                className="btn-primary"
                disabled={isGenerating}
              >
                {isGenerating ? "Generating..." : "Generate Outfit"}
              </button>
            </div>

            {/* Current Outfit */}
            {outfit && (
              <>
                <div className="section-header">
                  <h2 className="section-title">Your Outfit</h2>
                  <button onClick={saveToCloset} className="btn-secondary">
                    Save to Closet
                  </button>
                </div>

                <div className="outfit-grid">
                  {Object.entries(outfit).map(([slot, item]) => (
                    <div key={slot} className="outfit-card">
                      <div className="outfit-card-header">
                        <div className="slot-label">{slot}</div>
                      </div>
                      <div className="image-container">
                        <img
                          src={`${API_BASE}/images/${item.image}`}
                          alt={slot}
                          className="outfit-image"
                        />
                      </div>
                      <div className="outfit-card-actions">
                        <button
                          onClick={() => getAlternatives(slot)}
                          className="btn-secondary"
                          style={{ width: '100%' }}
                          disabled={isLoadingAlternatives && activeSlot === slot}
                        >
                          {isLoadingAlternatives && activeSlot === slot ? "Loading..." : "Change"}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}

            {/* Alternatives */}
            {alternatives.length > 0 && (
              <div className="alternatives-section">
                <h3 className="alternatives-title">Alternatives for {activeSlot}</h3>

                <div className="alternatives-grid">
                  {alternatives.map((item, idx) => (
                    <div
                      key={idx}
                      className="alternative-card"
                      onClick={() => applyAlternative(item)}
                    >
                      <img
                        src={`${API_BASE}/images/${item.image}`}
                        alt="alternative"
                        className="alternative-image"
                      />
                      <div className="score-label">
                        Score: {item.score.toFixed(3)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        ) : (
          <>
            {/* Digital Closet Section */}
            <div className="section-header">
              <h2 className="section-title">My Digital Closet</h2>
              <p className="section-subtitle">Your saved outfit combinations</p>
            </div>

            {savedOutfits.length === 0 ? (
              <div className="empty-state">
                <h3 className="empty-state-title">Your closet is empty</h3>
                <p className="empty-state-text">Generate and save outfits to build your digital wardrobe</p>
              </div>
            ) : (
              <div className="outfit-grid">
                {savedOutfits.map((saved) => (
                  <div key={saved.id} className="saved-outfit-card">
                    <div className="saved-outfit-header">
                      <div>
                        {editingOutfitId === saved.id ? (
                          <input
                            type="text"
                            className="rename-input"
                            value={editingName}
                            onChange={(e) => setEditingName(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && confirmRename()}
                            onBlur={confirmRename}
                            autoFocus
                          />
                        ) : (
                          <div
                            className="saved-outfit-name"
                            onClick={() => renameOutfit(saved.id)}
                            title="Click to rename"
                          >
                            {saved.name || `Outfit - ${new Date(saved.savedAt).toLocaleDateString()}`}
                          </div>
                        )}
                        <div className="saved-outfit-meta">
                          {saved.context.gender} · {saved.context.season} · {saved.context.occasion}
                        </div>
                        <div className="saved-outfit-date">
                          {new Date(saved.savedAt).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                    <div className="saved-outfit-items">
                      {Object.entries(saved.outfit).map(([slot, item]) => (
                        <div key={slot} className="saved-item">
                          <div className="saved-item-label">{slot}</div>
                          <img
                            src={`${API_BASE}/images/${item.image}`}
                            alt={slot}
                            className="saved-item-image"
                          />
                        </div>
                      ))}
                    </div>
                    <div className="saved-outfit-actions">
                      <button
                        onClick={() => deleteFromCloset(saved.id)}
                        className="btn-icon"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {/* Naming Modal */}
      {showNameModal && (
        <div className="modal-overlay" onClick={() => setShowNameModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3 className="modal-title">Name Your Outfit</h3>
            <input
              type="text"
              className="modal-input"
              placeholder="Enter outfit name (optional)"
              value={outfitName}
              onChange={(e) => setOutfitName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && confirmSaveOutfit()}
              autoFocus
            />
            <div className="modal-actions">
              <button onClick={() => setShowNameModal(false)} className="btn-secondary">
                Cancel
              </button>
              <button onClick={confirmSaveOutfit} className="btn-primary">
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default App;
