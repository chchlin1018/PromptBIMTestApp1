#pragma once
/// @file BIMTypes.h
/// @brief Common BIM type definitions — EntityType enum, Vec3, and utilities.
/// No Qt dependency. Used by all bim_core modules.

#include <string>
#include <cmath>

namespace bim {

/// @brief 22 BIM Entity Types covering structural, architectural, and MEP categories.
///
/// Structural: Wall, Slab, Column, Beam, Roof (load-bearing elements)
/// Architectural: Door, Window, Stair, Elevator, Ramp (access & enclosure)
/// MEP - HVAC: Chiller, CoolingTower, AHU, Fan (heating/ventilation/cooling)
/// MEP - Piping: Pump, Pipe, Valve (fluid transport)
/// MEP - Electrical: Duct, Cable, Sensor, ExhaustStack (distribution & monitoring)
/// Generic: fallback for unclassified entities
enum class EntityType {
    Wall,          ///< Vertical structural/partition element
    Slab,          ///< Horizontal floor/ceiling element
    Column,        ///< Vertical load-bearing member
    Beam,          ///< Horizontal spanning member
    Roof,          ///< Top enclosure element
    Door,          ///< Openable access element
    Window,        ///< Glazed opening element
    Stair,         ///< Vertical circulation (steps)
    Elevator,      ///< Vertical mechanical transport
    Ramp,          ///< Inclined access surface
    Chiller,       ///< Refrigeration unit (HVAC)
    CoolingTower,  ///< Heat rejection equipment (HVAC)
    AHU,           ///< Air Handling Unit (HVAC)
    Pump,          ///< Fluid circulation device
    Fan,           ///< Air circulation device
    Pipe,          ///< Fluid conduit
    Duct,          ///< Air conduit
    Cable,         ///< Electrical conductor
    Valve,         ///< Flow control device
    Sensor,        ///< Monitoring/measurement device
    ExhaustStack,  ///< Ventilation exhaust outlet
    Generic        ///< Unclassified fallback type
};

constexpr int ENTITY_TYPE_COUNT = 22;

[[nodiscard]] inline const char* entityTypeName(EntityType t) noexcept {
    switch (t) {
        case EntityType::Wall:          return "Wall";
        case EntityType::Slab:          return "Slab";
        case EntityType::Column:        return "Column";
        case EntityType::Beam:          return "Beam";
        case EntityType::Roof:          return "Roof";
        case EntityType::Door:          return "Door";
        case EntityType::Window:        return "Window";
        case EntityType::Stair:         return "Stair";
        case EntityType::Elevator:      return "Elevator";
        case EntityType::Ramp:          return "Ramp";
        case EntityType::Chiller:       return "Chiller";
        case EntityType::CoolingTower:  return "CoolingTower";
        case EntityType::AHU:           return "AHU";
        case EntityType::Pump:          return "Pump";
        case EntityType::Fan:           return "Fan";
        case EntityType::Pipe:          return "Pipe";
        case EntityType::Duct:          return "Duct";
        case EntityType::Cable:         return "Cable";
        case EntityType::Valve:         return "Valve";
        case EntityType::Sensor:        return "Sensor";
        case EntityType::ExhaustStack:  return "ExhaustStack";
        case EntityType::Generic:       return "Generic";
    }
    return "Unknown";
}

[[nodiscard]] inline EntityType entityTypeFromString(const std::string& s) noexcept {
    if (s == "Wall")          return EntityType::Wall;
    if (s == "Slab")          return EntityType::Slab;
    if (s == "Column")        return EntityType::Column;
    if (s == "Beam")          return EntityType::Beam;
    if (s == "Roof")          return EntityType::Roof;
    if (s == "Door")          return EntityType::Door;
    if (s == "Window")        return EntityType::Window;
    if (s == "Stair")         return EntityType::Stair;
    if (s == "Elevator")      return EntityType::Elevator;
    if (s == "Ramp")          return EntityType::Ramp;
    if (s == "Chiller")       return EntityType::Chiller;
    if (s == "CoolingTower")  return EntityType::CoolingTower;
    if (s == "AHU")           return EntityType::AHU;
    if (s == "Pump")          return EntityType::Pump;
    if (s == "Fan")           return EntityType::Fan;
    if (s == "Pipe")          return EntityType::Pipe;
    if (s == "Duct")          return EntityType::Duct;
    if (s == "Cable")         return EntityType::Cable;
    if (s == "Valve")         return EntityType::Valve;
    if (s == "Sensor")        return EntityType::Sensor;
    if (s == "ExhaustStack")  return EntityType::ExhaustStack;
    return EntityType::Generic;
}

struct Vec3 {
    double x = 0.0, y = 0.0, z = 0.0;

    Vec3() noexcept = default;
    Vec3(double x_, double y_, double z_) noexcept : x(x_), y(y_), z(z_) {}

    [[nodiscard]] Vec3 operator+(const Vec3& o) const noexcept { return {x + o.x, y + o.y, z + o.z}; }
    [[nodiscard]] Vec3 operator-(const Vec3& o) const noexcept { return {x - o.x, y - o.y, z - o.z}; }
    [[nodiscard]] Vec3 operator*(double s) const noexcept { return {x * s, y * s, z * s}; }

    [[nodiscard]] double length() const noexcept { return std::sqrt(x * x + y * y + z * z); }
    [[nodiscard]] double distanceTo(const Vec3& o) const noexcept { return (*this - o).length(); }
    [[nodiscard]] double dot(const Vec3& o) const noexcept { return x * o.x + y * o.y + z * o.z; }
    [[nodiscard]] Vec3 cross(const Vec3& o) const noexcept {
        return {y * o.z - z * o.y, z * o.x - x * o.z, x * o.y - y * o.x};
    }
};

} // namespace bim
