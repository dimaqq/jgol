# JGOL Worker Charm - AI Instructions

## Project Overview

This repository contains the **Worker charm** for JGOL (Juju Game of Life) - a distributed implementation of Conway's Game of Life designed to exercise Juju's orchestration capabilities. Each unit in the deployment represents a single cell in the Game of Life grid.

## System Architecture

The system consists of **two** charms working together:

### 1. Worker Charm (This Repository)
- **Role**: Implements the Game of Life cells and coordination logic
- **Responsibilities**:
  - Each unit represents one cell in the grid
  - Uses a **peer relation** to communicate with other worker units
  - The **leader unit** runs additional "god" code that:
    - Manages the global topology map of the grid
    - Coordinates game generations
    - Distributes state information to all cells
  - Non-leader units act as individual cells that:
    - Receive topology and state from the leader
    - Calculate their next generation state based on Conway's rules
    - Report updated state back through the peer relation

### 2. Coordinator Charm (Separate Repository)
- **Role**: Runs only the "god" code for managing the game
- **Responsibilities**:
  - Maintains the global grid topology
  - Coordinates game iterations
  - Distributes state to worker units
  - No individual cell logic - pure coordination

## Key Architecture Differences

- **Worker charm**: Dual-purpose - cells + optional god mode (leader unit)
- **Coordinator charm**: Single-purpose - only god/coordination logic
- Both use the `world` relation endpoint to communicate
- Workers use peer relations to communicate among themselves

## Conway's Game of Life Rules

Each worker unit implements these rules:
- **Birth**: A dead cell with exactly 3 live neighbors becomes alive
- **Survival**: A live cell with 2 or 3 live neighbors stays alive  
- **Death**: All other cases result in a dead cell

## Data Flow (Worker Charm with Peer Relations)

```
┌──────────────────────────────────────┐
│        Worker Charm Deployment        │
│                                       │
│  ┌─────────────────────────────────┐ │
│  │  Leader Unit (app/0)            │ │
│  │  • Cell logic                   │ │
│  │  • God code (topology & state)  │ │
│  └────────┬────────────────────────┘ │
│           │ peer relation            │
│           │ (topology map + state)   │
│      ┌────┴────┬────────┬───────┐   │
│      ↓         ↓        ↓       ↓   │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌────┐ │
│  │app/1 │ │app/2 │ │app/3 │ │... │ │
│  │Cell  │ │Cell  │ │Cell  │ │Cell│ │
│  └──────┘ └──────┘ └──────┘ └────┘ │
└──────────────────────────────────────┘
```

## Data Flow Steps

1. Leader unit publishes topology map (neighbor relationships) to peer relation
2. Leader distributes current generation state to all units
3. Each unit calculates its next state based on neighbors' states from the map
4. Units report their new state back through peer relation
5. Leader synchronizes the new generation and repeats

## Testing Approach

Tests use a 3x3 grid topology where each cell knows its neighbors:
```
0 1 2
3 4 5
6 7 8
```

- Unit 4 (center cell) has all 8 possible neighbors, making it ideal for comprehensive testing
- Tests verify the `world` relation for communication with coordinator
- The `remote_app_data` simulates data from either the coordinator charm or the leader unit

## Key Implementation Details

- Uses `ops` framework for charm development
- Topology map format: `{"app/0": ["app/1", "app/3", ...], ...}`
- State format: Individual keys per unit (e.g., `"app/4": "1"` for alive, `"0"` for dead)
- Relation endpoint: `world`
- Communication: JSON-encoded data through Juju relations