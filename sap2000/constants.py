#!/usr/bin/env python

FRAME_TYPES = {
  "PortalFrame" : 0,
  "ConcentricBraced" : 1,
  "EccentricBraced" : 2}

EFRAME_TYPES = {
  0 : "PortalFrame",
  1 : "ConcentricBraced",
  2 : "EccentricBraced"}

UNITS = {
  "lb_in_F" : 1,
  "lb_ft_F" : 2,
  "kip_in_F" : 3,
  "kip_ft_F" : 4,
  "kN_mm_C" : 5,
  "kN_m_C" : 6,
  "kgf_mm_C" : 7,
  "kgf_m_C" : 8,
  "N_mm_C" : 9,
  "N_m_C" : 10,
  "Ton_mm_C" : 11,
  "Ton_m_C" : 12,
  "kN_cm_C" : 13,
  "kgf_cm_C" : 14,
  "N_cm_C" : 15,
  "Ton_cm_C" : 16}

EUNITS = {
  1 : "lb_in_F",
  2 : "lb_ft_F",
  3 : "kip_in_F",
  4 : "kip_ft_F",
  5 : "kN_mm_C",
  6 : "kN_m_C",
  7 : "kgf_mm_C",
  8 : "kgf_m_C",
  9 : "N_mm_C",
  10 : "N_m_C",
  11 : "Ton_mm_C",
  12 : "Ton_m_C",
  13 : "kN_cm_C",
  14 : "kgf_cm_C",
  15 : "N_cm_C",
  16 :"Ton_cm_C"}

MATERIAL_TYPES = {
  "MATERIAL_STEEL" : 1,
  "MATERIAL_CONCRETE" : 2,
  "MATERIAL_NODESIGN" : 3,
  "MATERIAL_ALUMINUM" : 4,
  "MATERIAL_COLDFORMED" : 5,
  "MATERIAL_REBAR" : 6,
  "MATERIAL_TENDON" : 7}

EMATERIAL_TYPES = {
  1 : "MATERIAL_STEEL",
  2 : "MATERIAL_CONCRETE",
  3 : "MATERIAL_NODESIGN",
  4 : "MATERIAL_ALUMINUM",
  5 : "MATERIAL_COLDFORMED",
  6 : "MATERIAL_REBAR",
  7 : "MATERIAL_TENDON"}
        
EOBJECT_TYPES = {
  1 : "points",
  2 : "frames",
  3 : "cables",
  4 : "tendons",
  5 : "areas",
  6 : "solids",
  7 : "links"}

OBJECT_TYPES = {
  "points": 1,
  "frames": 2,
  "cables": 3,
  "tendons": 4,
  "areas": 5,
  "solids": 6,
  "links": 7}

LOAD_PATTERN_TYPES = {
  'LTYPE_DEAD' : 1,
  'LTYPE_SUPERDEAD' : 2,
  'LTYPE_LIVE' : 3,
  'LTYPE_REDUCELIVE' : 4,
  'LTYPE_QUAKE' : 5,
  'LTYPE_WIND': 6,
  'LTYPE_SNOW' : 7,
  'LTYPE_OTHER' : 8,
  'LTYPE_MOVE' : 9,
  'LTYPE_TEMPERATURE' : 10,
  'LTYPE_ROOFLIVE' : 11,
  'LTYPE_NOTIONAL' : 12,
  'LTYPE_PATTERNLIVE' : 13,
  'LTYPE_WAVE': 14,
  'LTYPE_BRAKING' : 15,
  'LTYPE_CENTRIFUGAL' : 16,
  'LTYPE_FRICTION' : 17,
  'LTYPE_ICE' : 18,
  'LTYPE_WINDONLIVELOAD' : 19,
  'LTYPE_HORIZONTALEARTHPRESSURE' : 20,
  'LTYPE_VERTICALEARTHPRESSURE' : 21,
  'LTYPE_EARTHSURCHARGE' : 22,
  'LTYPE_DOWNDRAG' : 23,
  'LTYPE_VEHICLECOLLISION' : 24,
  'LTYPE_VESSELCOLLISION' : 25,
  'LTYPE_TEMPERATUREGRADIENT' : 26,
  'LTYPE_SETTLEMENT' : 27,
  'LTYPE_SHRINKAGE' : 28,
  'LTYPE_CREEP' : 29,
  'LTYPE_WATERLOADPRESSURE' : 30,
  'LTYPE_LIVELOADSURCHARGE' : 31,
  'LTYPE_LOCKEDINFORCES' : 32,
  'LTYPE_PEDESTRIANLL' : 33,
  'LTYPE_PRESTRESS' : 34,
  'LTYPE_HYPERSTATIC' : 35,
  'LTYPE_BOUYANCY' : 36,
  'LTYPE_STREAMFLOW' : 37,
  'LTYPE_IMPACT' : 38,
  'LTYPE_CONSTRUCTION' : 39,
}