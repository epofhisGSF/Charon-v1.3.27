# CHARON v1.3.18 - Routing Enhancements

## 🎯 **New Features**

### 1. **Realistic Multi-Hop Penalties**
### 2. **Jumpbridge Network Support**

---

## 🔥 **Multi-Hop Deprioritization**

### The Problem:
Previously, multi-hop wormholes got a -5 bonus, making them seem attractive.

**Reality Check:**
- **Burn Time:** Each intermediate WH system requires warping to the hole (2-5 minutes)
- **NPC Danger:** Drifter systems have aggressive NPCs that can kill you
- **Complexity:** More transitions = more points of failure
- **Multiple Risks:** Two holes instead of one means 2x the chance of hole collapse

### The Solution:
Multi-hop now gets **+30 penalty** instead of -5 bonus:
```python
BURN_TIME_PENALTY = 15      # Each WH system requires burn time
NPC_DANGER_PENALTY = 10     # Risk of NPCs in each system  
COMPLEXITY_PENALTY = 5      # More moving parts = more failure
```

### What This Means:
Multi-hop routes only preferred when they save **MASSIVE** gate jumps (30+)

**Example:**
```
Route A: 10 gates via single WH
Route B: 5 gates via 2-hop WH chain

Old scoring:
A: 10 gates = 10 points
B: 5 gates - 5 (multi-hop bonus) = 0 points ← B wins!

New scoring:
A: 10 gates = 10 points
B: 5 gates + 30 (burn penalty) = 35 points ← A wins!
```

**Result:** Single-hop + more gates >>> Multi-hop + fewer gates

---

## 🌉 **Jumpbridge Support**

### What Are Jumpbridges?
Alliance-owned structures that provide instant travel between systems.

**Benefits:**
- Instant travel (no gate animation)
- Skip hostile gates
- Much faster than normal gates

### How It Works:

**1. Configure Your Jumpbridge Network**

Edit `jumpbridges.py`:
```python
JUMPBRIDGES = [
    # Format: ('System 1', 'System 2', 'Alliance'),
    ('1DQ1-A', 'PUIG-F', 'GSF'),
    ('PUIG-F', 'HY-RWO', 'GSF'),
    ('T5ZI-S', 'E3OI-U', 'GSF'),
    # Add your alliance's jumpbridges here
]
```

**2. Automatic Integration**

CHARON loads jumpbridges on startup:
```
✓ Loaded 15 jumpbridge connections
```

**3. Weighted Pathfinding**

Routing now uses **costs**:
- **Standard gate:** 1.0 cost
- **Jumpbridge:** 0.3 cost (70% faster!)

**Example Route:**
```
Delve to Querious:

Old route (gates only):
1DQ1-A → T5ZI-S → E3OI-U → ... → D-W7F0
= 25 gates = 25.0 cost

New route (with JBs):
1DQ1-A → [JB] → PUIG-F → [JB] → HY-RWO → ... → D-W7F0
= 2 JBs + 10 gates = 0.6 + 10.0 = 10.6 cost ← Much better!
```

### Getting Your JB Network:

**Goonswarm:**
- Check alliance forums/wiki
- Ask in Intel channels
- Use dotlan.net filters

**Update Process:**
1. Get latest JB list from your alliance
2. Edit `jumpbridges.py`
3. Add entries in format: `('System A', 'System B', 'Tag')`
4. Restart CHARON
5. JBs automatically integrated!

### Verification:

Check console on startup:
```
✓ Loaded 8,285 solar systems
✓ Loaded 48 special edition ships
✓ Loaded 15 jumpbridge connections  ← Your JBs loaded!
```

---

## 📊 **Routing Algorithm Changes**

### Old Algorithm (BFS):
- Breadth-first search
- All jumps cost the same
- Simple but not realistic

### New Algorithm (Dijkstra with Weights):
- Weighted pathfinding
- Gates cost 1.0, JBs cost 0.3
- Finds truly optimal routes
- Considers travel time, not just jump count

---

## 🎯 **Practical Examples**

### Example 1: Pure Gate Route
```
Jita → Amarr (no WHs, no JBs)
Result: 9 gates via normal route
Score: 9.0
```

### Example 2: WH Route
```
Jita → Amarr via Fresh WH in Perimeter → Sarum Prime
Entry: 2 gates
Exit: 3 gates
WH: Fresh, 100% mass
Score: 2 + 3 = 5.0 ← Better than 9 gates!
```

### Example 3: Multi-Hop WH (Now Realistic)
```
Jita → Amarr via 2-hop WH chain
Entry: 1 gate
Hop 1: Burn time + NPCs
Hop 2: Burn time + NPCs
Exit: 2 gates
Score: 1 + 30 (penalty) + 2 = 33.0 ← Worse than single-hop!
```

### Example 4: JB Enhanced Route
```
1DQ1-A → D-W7F0 with JBs
Path: 1DQ → [JB:0.3] → PUIG-F → [JB:0.3] → HY-RWO → [7 gates] → D-W7F0
Cost: 0.3 + 0.3 + 7.0 = 7.6

Without JBs: 25 gates = 25.0 cost

Savings: 70% faster!
```

---

## ⚙️ **Configuration**

### Jumpbridge Settings (jumpbridges.py):

```python
# Travel time assumptions (seconds)
JB_ACTIVATION_TIME = 10      # Time to activate and jump
JB_GATE_COMPARISON = 0.3     # Count as 30% of a gate

# System name format
# MUST match EVE exactly (case-sensitive!)
('1DQ1-A', 'PUIG-F', 'GSF')  # ✅ Correct
('1dq1-a', 'puig-f', 'gsf')  # ❌ Wrong case
('1DQ', 'PUIG', 'GSF')       # ❌ Wrong format
```

### Multi-Hop Penalties (drifter_tracker.py):

Already configured optimally. If you want to tweak:
```python
BURN_TIME_PENALTY = 15       # Time to burn to WH
NPC_DANGER_PENALTY = 10      # NPC risk
COMPLEXITY_PENALTY = 5       # Failure risk
```

---

## 🚀 **Using The New Features**

### Standard Workflow:

1. **First Time Setup:**
   - Get your alliance JB network
   - Edit `jumpbridges.py`
   - Save file

2. **Normal Use:**
   - CHARON loads JBs automatically
   - Routing uses JBs when beneficial
   - Multi-hop deprioritized realistically

3. **Route Display:**
   - Routes show total "cost" not just jump count
   - JB routes clearly better (lower cost)
   - Multi-hop only shown when truly worth it

---

## 📝 **Technical Details**

### Pathfinding Algorithm:

**Old:** Simple BFS
```
All edges cost 1
Find shortest path by jump count
```

**New:** Weighted Dijkstra
```
Gate edges cost 1.0
JB edges cost 0.3
Find shortest path by total cost
```

### Multi-Hop Scoring:

**Old Formula:**
```
score = total_gates - 5 (bonus)
```

**New Formula:**
```
score = total_gates + 30 (penalty for burn/danger/complexity)
```

---

## 💡 **Tips & Tricks**

### For Null-Sec Alliances:
1. Keep `jumpbridges.py` updated with latest JB network
2. Share file with corpmates
3. Update after sov changes

### For WH Operations:
1. Multi-hop now realistic - don't expect miracles
2. Single fresh WH + gates often better than 2-hop
3. Burn time matters!

### For Route Planning:
1. Check multiple routes
2. JB routes will show lowest cost
3. Multi-hop only if HUGE gate savings (30+)

---

## 🔧 **Troubleshooting**

### "No JBs loaded"
- Check `jumpbridges.py` exists
- Verify system names match EVE exactly
- Case-sensitive!

### "Multi-hop still showing first"
- Check WH status (Critical holes heavily penalized)
- Verify gate counts are accurate
- May still be best route if saves 40+ gates

### "JBs not used in routes"
- Verify JB systems are in route path
- Check spelling in `jumpbridges.py`
- Restart CHARON after editing JB file

---

**CHARON v1.3.18 - Realistic Routing**

Multi-hop deprioritized. Jumpbridges integrated. Routes actually useful now. o7 ⚙️🌉
