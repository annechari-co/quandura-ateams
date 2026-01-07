# Quandura Field App Specification

Technical specification for the Safety Inspection Field Application.

## Overview

Mobile-first application for conducting facility safety inspections. Produces professional inspection reports matching the RiskI Report format (see `Risk Inspection Report Dayton_Fleet V3.0_signed.pdf`).

**MVP Scope:** Facility Inspections (walkthrough identifying hazards)
**Future:** Field Inspections (evaluating active jobsite operations like trenching)

---

## Core Concepts

### Inspection Types

| Type | Description | MVP |
|------|-------------|-----|
| Facility Inspection | Walk through building to identify hazards and compliance issues | Yes |
| Field Inspection | Evaluate active work operations (trenching, electrical, etc.) | No |

### Two Distinct Outputs

```
Room Inventory → Generates Checklist → Inspector Evaluates
                                              ↓
                    ┌─────────────────────────┴─────────────────────────┐
                    ↓                                                   ↓
           ALL Results                                          FAILURES Only
                    ↓                                                   ↓
        Appendix B: Self-Inspection Form                    Table 1: Findings
        (Proof of due diligence)                            (Corrective actions)
```

**Appendix B** = Complete record of everything inspected (pass and fail)
**Table 1** = Only items requiring corrective action

---

## User Roles (RBAC)

| Role | Permissions |
|------|-------------|
| Basic User | Read inspection reports |
| Coordinator | Read + Schedule inspections |
| Compliance Officer | Read + Write + Conduct inspections + Generate reports |
| Admin | Full access + User management + System config |

---

## Inspection Workflow

### 1. Pre-Inspection Setup

```
New Inspection
     ↓
Select Facility (from facility registry)
     ↓
Enter inspection metadata:
  - Date/Time
  - Inspector name(s)
  - Inspection type (Annual, Follow-up, Complaint-based, etc.)
  - Weather conditions (if applicable)
     ↓
Load or Create Floor Plan
```

### 2. Floor Plan Management

**Initial Setup (First Visit):**
- Upload floor plan image (PDF, PNG, JPG)
- MVP: Manual room boundary definition
- Future: AI simplification via Nano Banana

**Floor Plan Interaction:**
- Pan and zoom
- Long-press to access pin menu
- Tap room to enter room inspection mode

### 3. Room Inventory Cataloging

When inspector enters a room for the first time:

```
Long-press on room → "Catalog Room"
     ↓
Room Details:
  - Name: "Room 102"
  - Description: "Maintenance Shop"
  - Room Type: [Dropdown]
     ↓
Equipment Present: (searchable, multi-select)
  ☑ Fire Extinguisher (qty: 2)
  ☑ Flammables Cabinet (qty: 1)
  ☑ Electrical Panel (qty: 1)
  ☐ Eye Wash Station
  ☐ First Aid Kit
  ☐ AED
  ☐ Compressed Gas Cylinders
  ☐ Chemical Storage
  ... (full list below)
     ↓
Pin each item on floor plan (optional)
Add photo of item (optional)
Add location notes (optional)
```

**If room has no significant equipment:**
- Select "General Space" or leave equipment list empty
- Room still gets baseline checklist
- Room still appears in Appendix B

### 4. Dynamic Checklist Generation

Checklist = Baseline Items + Equipment-Specific Items

**Baseline Checklist (applies to ALL rooms):**

| Item | Criteria |
|------|----------|
| Egress | Path clear, door operational, signage visible |
| Trip Hazards | Floor clear of cords, debris, uneven surfaces |
| Lighting | Adequate illumination, fixtures secure |
| Ceiling/Walls | No damage, stains, or deterioration |
| Floor Condition | No cracks, holes, or damage |
| Water Damage | No visible leaks, stains, or mold |
| Storage | Items stored safely, not blocking egress |

**Room Type Additions:**

| Room Type | Additional Baseline Items |
|-----------|--------------------------|
| Office | Ergonomics, electrical cord management |
| Kitchen/Break Room | Appliance condition, food storage |
| Restroom | Fixture condition, ADA compliance, supplies |
| Mechanical Room | Access restricted, equipment guarding |
| Storage | Weight limits, stacking safety |

**Equipment-Specific Items:** See Equipment Types section below.

### 5. Conducting the Inspection

```
Select Room on Floor Plan
     ↓
View Generated Checklist for Room
     ↓
For Each Item:
  ├── Pass ✓
  ├── Fail ✗ → Capture Finding
  └── N/A (not applicable today)
     ↓
If Fail:
  - Take photo (required)
  - Select priority (High-Immediate, High-30, Medium-60, Low-90)
  - Add description
  - Add recommendation
  - Link regulatory citation (optional, from predefined list)
     ↓
Mark Room Complete → Move to Next Room
```

### 6. Finding Capture

When an item fails inspection:

```
Finding Details:
  - Finding ID: Auto-generated (Site-Location-Year-Seq)
    Example: Fleet-Dayton-2025-06

  - Location: Room name + specific location
    Example: "Room 102 - South wall"

  - Priority:
    ○ High (Immediate) - Life safety, requires immediate action
    ○ High (30 days) - Serious violation
    ○ Medium (60 days) - Moderate concern
    ○ Low (90 days) - Minor issue

  - Photo: Required (camera capture)

  - Description: What is wrong
    Example: "Fire extinguisher pressure gauge in red zone"

  - Recommendation: How to fix
    Example: "Service or replace fire extinguisher"

  - Regulatory Reference: (optional dropdown)
    Example: "NFPA 10, 7.2.1.2"

  - Responsible Party: Who should fix this
    ○ Location Staff
    ○ Facilities Management
    ○ IT/Technology
    ○ External Contractor
    ○ Other (specify)
```

### 7. Report Generation

After all rooms inspected:

```
Review Findings → Generate Report → Export PDF
```

**Report Structure (matching RiskI format):**

1. **Cover Page**
   - Facility photo
   - Facility name and address
   - Inspection date
   - Inspector name

2. **Executive Summary**
   - Priority breakdown table
   - Key concerns summary

3. **Table of Contents**

4. **Introduction**
   - Purpose and scope
   - Site information
   - Inspection attendees
   - Inspection type checkboxes

5. **Summary of Findings**
   - Narrative overview
   - **Table 1: Findings** (failures only)
     - Finding ID
     - Location
     - Priority
     - Regulatory Citations
     - Description
     - Recommendation
     - Timeline

6. **Floor Plan with Findings**
   - **Figure 3: Findings Map**
   - Color-coded pins by priority
   - Finding IDs labeled

7. **Corrective Actions by Responsible Party**
   - Grouped by who must fix
   - Timeline summary

8. **Conclusion**
   - Next steps
   - Re-inspection date
   - 14-day check-in commitment

9. **References**
   - Regulatory citations used

10. **Appendix A: Photograph Log**
    - All finding photos with captions
    - Photo ID linked to Finding ID

11. **Appendix B: Self-Inspection Form**
    - Room-by-room checklist results
    - ALL items (pass and fail)
    - Organized by room
    - Equipment-specific criteria shown

12. **Appendix C: Supporting Documents**
    - Fire Marshal reports (if applicable)
    - Previous inspection references

---

## Equipment Types and Inspection Criteria

### Fire Safety

**Fire Extinguisher**
| Criteria | Priority | Regulatory Ref |
|----------|----------|----------------|
| Pressure gauge in green zone | High | NFPA 10, 7.2.1.2 |
| Inspection tag current (< 12 months) | High | NFPA 10, 7.2.2 |
| Mounted at proper height (3.5-5 ft) | Medium | NFPA 10, 6.1.3 |
| Unobstructed (3 ft clearance) | High | NFPA 10, 6.1.3.8 |
| Signage visible | Medium | NFPA 10, 6.1.3.4 |
| No visible damage or corrosion | High | NFPA 10, 7.2.1.1 |
| Safety pin and tamper seal intact | Medium | NFPA 10, 7.2.1.3 |

**Exit Sign**
| Criteria | Priority | Regulatory Ref |
|----------|----------|----------------|
| Illuminated and visible | High | NFPA 101, 7.10 |
| Proper placement (above exit) | Medium | NFPA 101, 7.10.1.2 |
| Backup battery functional | High | NFPA 101, 7.10.4 |
| No obstructions | High | NFPA 101, 7.10.1.5 |

**Emergency Lighting**
| Criteria | Priority | Regulatory Ref |
|----------|----------|----------------|
| Monthly test button functional | Medium | NFPA 101, 7.9.3 |
| 90-second illumination test passed | High | NFPA 101, 7.9.3.1.1 |
| Covers clean and intact | Low | General |
| Proper aim/coverage | Medium | NFPA 101, 7.9.2.1 |

**Smoke Detector**
| Criteria | Priority | Regulatory Ref |
|----------|----------|----------------|
| Test button responsive | High | NFPA 72, 14.4.5 |
| No visible damage | High | NFPA 72, 14.4.5.2 |
| Not painted over | High | NFPA 72, 14.4.5.3 |
| Proper spacing maintained | Medium | NFPA 72, 17.7.3 |

**Sprinkler Head**
| Criteria | Priority | Regulatory Ref |
|----------|----------|----------------|
| 18" clearance below | High | NFPA 13, 8.5.5.1 |
| No paint or corrosion | High | NFPA 13, 4.1.5 |
| Correct orientation | High | NFPA 13, 8.4 |
| Escutcheon plate intact | Low | NFPA 13, 8.4.5 |

### Electrical

**Electrical Panel**
| Criteria | Priority | Regulatory Ref |
|----------|----------|----------------|
| 36" clearance maintained | High | NFPA 70, 110.26 |
| All breakers labeled | Medium | NFPA 70, 408.4 |
| Cover secured | High | NFPA 70, 408.38 |
| No exposed wiring | High | NFPA 70, 110.12 |
| No signs of overheating | High | NFPA 70, 110.14 |

**GFCI Outlet**
| Criteria | Priority | Regulatory Ref |
|----------|----------|----------------|
| Test button trips circuit | High | NFPA 70, 210.8 |
| Reset functions properly | High | NFPA 70, 210.8 |
| Cover plate intact | Low | NFPA 70, 406.6 |
| Properly located (wet areas) | High | NFPA 70, 210.8 |

**Extension Cord (Temporary)**
| Criteria | Priority | Regulatory Ref |
|----------|----------|----------------|
| Not daisy-chained | High | OSHA 1910.334(a)(1) |
| Properly rated for load | High | OSHA 1910.303(b)(2) |
| No damage to cord/plug | High | OSHA 1910.334(a)(2) |
| Not run through walls/ceilings | High | NFPA 70, 400.12 |
| Not used as permanent wiring | High | OSHA 1910.334(a)(1) |

### Chemical Storage

**Flammables Cabinet**
| Criteria | Priority | Regulatory Ref |
|----------|----------|----------------|
| Self-closing doors functional | High | NFPA 30, 9.5.3 |
| Properly grounded | High | NFPA 30, 9.5.4 |
| Contents match inventory | Medium | OSHA 1910.106(d)(3) |
| FM/UL listed label present | Medium | NFPA 30, 9.5.1 |
| No incompatible materials stored | High | OSHA 1910.106(d)(3) |
| Proper signage | Medium | NFPA 30, 9.7 |
| Not overfilled | High | NFPA 30, 9.5.2 |

**Compressed Gas Cylinders**
| Criteria | Priority | Regulatory Ref |
|----------|----------|----------------|
| Secured upright (chain/strap) | High | OSHA 1910.253(b)(2) |
| Caps in place when not in use | High | OSHA 1910.253(b)(2) |
| Proper segregation (O2 from fuel) | High | OSHA 1910.253(b)(4) |
| Current inspection date | Medium | OSHA 1910.253(b)(5) |
| Proper labeling | Medium | OSHA 1910.253(b)(1) |

**Chemical Storage Area**
| Criteria | Priority | Regulatory Ref |
|----------|----------|----------------|
| SDS readily accessible | High | OSHA 1910.1200(g) |
| Secondary containment present | High | EPA 40 CFR 264.175 |
| Proper labeling on containers | High | OSHA 1910.1200(f) |
| Incompatibles separated | High | OSHA 1910.106(d)(6) |
| Spill kit available | Medium | OSHA 1910.120(j) |
| Ventilation adequate | High | OSHA 1910.106(d)(4) |

### Emergency Equipment

**First Aid Kit**
| Criteria | Priority | Regulatory Ref |
|----------|----------|----------------|
| Contents present per checklist | Medium | OSHA 1910.151(b) |
| No expired items | Medium | ANSI Z308.1 |
| Easily accessible | Medium | OSHA 1910.151(b) |
| Signage visible | Low | General |

**AED (Automated External Defibrillator)**
| Criteria | Priority | Regulatory Ref |
|----------|----------|----------------|
| Status indicator shows ready | High | AHA Guidelines |
| Pads not expired | High | AHA Guidelines |
| Battery status OK | High | AHA Guidelines |
| Cabinet alarm functional | Medium | General |
| Signage visible | Medium | General |

**Eye Wash Station**
| Criteria | Priority | Regulatory Ref |
|----------|----------|----------------|
| Weekly activation test logged | High | ANSI Z358.1 |
| Water flow adequate | High | ANSI Z358.1, 4.5 |
| Unobstructed access | High | ANSI Z358.1, 4.5.5 |
| Within 10 seconds of hazard | High | ANSI Z358.1, 4.5.2 |
| Proper signage | Medium | ANSI Z358.1, 4.5.6 |

**Emergency Shower**
| Criteria | Priority | Regulatory Ref |
|----------|----------|----------------|
| Weekly activation test logged | High | ANSI Z358.1 |
| Water flow adequate (20 GPM) | High | ANSI Z358.1, 4.1.2 |
| Valve activates easily | High | ANSI Z358.1, 4.2.1 |
| Unobstructed access | High | ANSI Z358.1, 4.5.5 |
| Proper signage | Medium | ANSI Z358.1, 4.2.6 |

### Facility Systems

**HVAC Unit**
| Criteria | Priority | Regulatory Ref |
|----------|----------|----------------|
| Filter status (clean/changed) | Medium | General |
| No unusual noises | Low | General |
| Vents unobstructed | Medium | General |
| Thermostat functional | Low | General |
| Maintenance log current | Low | General |

**Water Heater**
| Criteria | Priority | Regulatory Ref |
|----------|----------|----------------|
| T&P valve present | High | NFPA 54, 10.11 |
| Discharge pipe installed | High | NFPA 54, 10.11.5 |
| No signs of corrosion/leaks | Medium | General |
| Seismic strapping (if required) | High | Local codes |
| Clearance maintained | Medium | NFPA 54, 10.6 |

**Elevator**
| Criteria | Priority | Regulatory Ref |
|----------|----------|----------------|
| Current inspection certificate | High | ASME A17.1 |
| Emergency phone functional | High | ASME A17.1, 2.27 |
| Door sensors operational | High | ASME A17.1, 2.13 |
| Cab lighting functional | Medium | ASME A17.1, 2.16 |
| Floor leveling accurate | Medium | ASME A17.1, 2.25 |

---

## Data Model

### Entities

```
Facility
  - id: UUID
  - tenant_id: UUID
  - name: string
  - address: string
  - floor_plans: FloorPlan[]
  - rooms: Room[]
  - created_at: timestamp
  - updated_at: timestamp

FloorPlan
  - id: UUID
  - facility_id: UUID
  - name: string (e.g., "Floor 1")
  - image_url: string
  - rooms: Room[]

Room
  - id: UUID
  - floor_plan_id: UUID
  - name: string (e.g., "Room 102")
  - description: string (e.g., "Maintenance Shop")
  - room_type: RoomType
  - boundary_coords: JSON (polygon on floor plan)
  - inventory: RoomInventoryItem[]

RoomType (enum)
  - GENERAL_SPACE
  - OFFICE
  - KITCHEN_BREAK_ROOM
  - RESTROOM
  - MECHANICAL_ROOM
  - STORAGE
  - WAREHOUSE
  - LABORATORY
  - CUSTOM

EquipmentType
  - id: UUID
  - name: string (e.g., "Fire Extinguisher")
  - category: string (e.g., "Fire Safety")
  - inspection_criteria: InspectionCriteria[]

InspectionCriteria
  - id: UUID
  - equipment_type_id: UUID
  - description: string
  - priority: Priority
  - regulatory_reference: string
  - frequency: Frequency

Priority (enum)
  - HIGH_IMMEDIATE
  - HIGH_30_DAYS
  - MEDIUM_60_DAYS
  - LOW_90_DAYS

Frequency (enum)
  - EVERY_INSPECTION
  - MONTHLY
  - QUARTERLY
  - ANNUAL

RoomInventoryItem
  - id: UUID
  - room_id: UUID
  - equipment_type_id: UUID
  - quantity: int
  - pin_location: JSON (x, y on floor plan)
  - notes: string
  - photo_url: string (optional)
  - created_at: timestamp

Inspection
  - id: UUID
  - facility_id: UUID
  - inspector_id: UUID
  - inspection_type: InspectionType
  - status: InspectionStatus
  - scheduled_date: date
  - completed_date: date
  - weather_conditions: string
  - attendees: string[]
  - checklist_results: ChecklistResult[]
  - findings: Finding[]

InspectionType (enum)
  - ANNUAL
  - FOLLOW_UP
  - COMPLAINT_BASED
  - SPECIAL_REQUEST
  - NEW_FACILITY

InspectionStatus (enum)
  - SCHEDULED
  - IN_PROGRESS
  - PENDING_REVIEW
  - COMPLETED

ChecklistResult
  - id: UUID
  - inspection_id: UUID
  - room_id: UUID
  - criteria_id: UUID (null for baseline items)
  - baseline_item: string (if criteria_id is null)
  - inventory_item_id: UUID (null for baseline)
  - result: Result
  - notes: string
  - timestamp: timestamp

Result (enum)
  - PASS
  - FAIL
  - NOT_APPLICABLE

Finding
  - id: UUID
  - inspection_id: UUID
  - finding_id: string (e.g., "Fleet-Dayton-2025-06")
  - room_id: UUID
  - checklist_result_id: UUID
  - location_detail: string
  - priority: Priority
  - description: string
  - recommendation: string
  - regulatory_reference: string
  - responsible_party: ResponsibleParty
  - photo_urls: string[]
  - pin_location: JSON
  - timeline_days: int
  - status: FindingStatus

ResponsibleParty (enum)
  - LOCATION_STAFF
  - FACILITIES_MANAGEMENT
  - IT_TECHNOLOGY
  - EXTERNAL_CONTRACTOR
  - OTHER

FindingStatus (enum)
  - OPEN
  - IN_PROGRESS
  - PENDING_VERIFICATION
  - CLOSED
```

### Relationships

```
Facility 1──∞ FloorPlan
FloorPlan 1──∞ Room
Room ∞──∞ EquipmentType (via RoomInventoryItem)
EquipmentType 1──∞ InspectionCriteria
Facility 1──∞ Inspection
Inspection 1──∞ ChecklistResult
Inspection 1──∞ Finding
ChecklistResult 1──0..1 Finding
```

---

## API Endpoints (Draft)

### Facilities
- `GET /facilities` - List facilities for tenant
- `POST /facilities` - Create facility
- `GET /facilities/{id}` - Get facility with floor plans
- `PUT /facilities/{id}` - Update facility
- `DELETE /facilities/{id}` - Archive facility

### Floor Plans
- `POST /facilities/{id}/floor-plans` - Upload floor plan
- `GET /facilities/{id}/floor-plans/{fp_id}` - Get floor plan with rooms
- `PUT /floor-plans/{id}/rooms` - Update room boundaries

### Room Inventory
- `GET /rooms/{id}` - Get room with inventory
- `POST /rooms/{id}/inventory` - Add equipment to room
- `PUT /rooms/{id}/inventory/{item_id}` - Update inventory item
- `DELETE /rooms/{id}/inventory/{item_id}` - Remove inventory item

### Equipment Types
- `GET /equipment-types` - List all equipment types with criteria
- `GET /equipment-types/{id}/criteria` - Get inspection criteria for type

### Inspections
- `POST /inspections` - Create new inspection
- `GET /inspections/{id}` - Get inspection with results
- `PUT /inspections/{id}` - Update inspection metadata
- `POST /inspections/{id}/start` - Begin inspection
- `POST /inspections/{id}/complete` - Mark inspection complete

### Checklist
- `GET /inspections/{id}/rooms/{room_id}/checklist` - Get generated checklist for room
- `POST /inspections/{id}/results` - Submit checklist results
- `PUT /inspections/{id}/results/{result_id}` - Update result

### Findings
- `POST /inspections/{id}/findings` - Create finding from failed result
- `GET /inspections/{id}/findings` - List findings
- `PUT /findings/{id}` - Update finding
- `POST /findings/{id}/photos` - Upload finding photo

### Reports
- `GET /inspections/{id}/report` - Generate PDF report
- `GET /inspections/{id}/report/preview` - Preview report data

---

## UI Screens

### Mobile (Inspector)

1. **Dashboard**
   - Upcoming inspections
   - In-progress inspections
   - Recent completions

2. **Inspection Detail**
   - Facility info
   - Progress indicator (rooms completed / total)
   - Start/Resume button

3. **Floor Plan View**
   - Interactive floor plan
   - Room status indicators (not started, in progress, complete)
   - Finding pins (color by priority)
   - Tap room to inspect
   - Long-press for menu

4. **Room Inspection**
   - Room name and type
   - Checklist items (baseline + equipment)
   - Pass/Fail/NA buttons
   - Quick photo capture
   - Notes field

5. **Finding Capture**
   - Photo capture (required)
   - Priority selector
   - Description field
   - Recommendation field
   - Regulatory reference dropdown
   - Responsible party selector

6. **Room Inventory** (setup mode)
   - Equipment type search/select
   - Quantity input
   - Pin placement on floor plan
   - Photo capture (optional)

7. **Inspection Review**
   - Summary of findings by priority
   - Room completion status
   - Generate report button

### Web (Admin/Coordinator)

1. **Facility Management**
   - Facility list
   - Floor plan upload
   - Room definition tool

2. **Inspection Scheduling**
   - Calendar view
   - Assign inspectors
   - Set inspection type

3. **Report Viewer**
   - Generated reports
   - Export options
   - Comparison with previous inspections

4. **Finding Tracking**
   - Open findings dashboard
   - Filter by facility, priority, responsible party
   - Status updates

---

## Future Enhancements

1. **Field Inspections** - Jobsite evaluation checklists (trenching, excavation, electrical work)
2. **Offline Mode** - Local storage with sync when connected
3. **EAP Integration** - Emergency Action Plans linked to facilities
4. **AI Floor Plan Processing** - Nano Banana integration for automatic room detection
5. **Automated Scheduling** - Based on facility risk profile and history
6. **Integration with Corrective Action System** - Work order generation
7. **Multi-language Support** - Spanish, etc.
8. **Voice Notes** - Audio recording for findings

---

## Technical Considerations

### Performance
- Floor plan images optimized for mobile (tiles for large plans)
- Checklist generation cached after first build per room
- Photo compression before upload

### Security
- All data tenant-isolated (RLS)
- Photos stored in tenant-specific buckets
- Audit log for all inspection activities

### Compliance
- Data retention per government requirements
- Export capabilities for legal discovery
- Chain of custody for finding photos
