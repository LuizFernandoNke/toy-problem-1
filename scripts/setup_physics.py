import sys
from pathlib import Path

# Add root directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.simulation_config import SimulationConfig

def setup_physics_files(cfg: SimulationConfig, case_dir: Path):
    """Generates 0/U, 0/p_rgh, 0/alpha.water, 0/alpha.air, and constant/phaseProperties for interFoam."""
    
    zero_dir = case_dir / "0"
    zero_dir.mkdir(parents=True, exist_ok=True)

    # Remove arquivos obsoletos da simulação anterior (incluindo o transportProperties se houver)
    for obsolete_file in ["p", "turbulenceProperties", "momentumTransport"]:
        obs_path = zero_dir / obsolete_file
        if obs_path.exists():
            obs_path.unlink()

    trans_legacy = case_dir / "constant" / "transportProperties"
    if trans_legacy.exists():
        trans_legacy.unlink()

    # 1. Write constant/phaseProperties (Two-phase properties for water and air)
    phase_props = f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2606                                  |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M manipulation |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      phaseProperties;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

phases (water air);

water
{{
    transportModel  Newtonian;
    nu              {cfg.kinematic_viscosity:.7e};
    rho             1000;
}}

air
{{
    transportModel  Newtonian;
    nu              1.48e-05;
    rho             1.2;
}}

// ************************************************************************* //
"""
    phase_path = case_dir / "constant" / "phaseProperties"
    phase_path.parent.mkdir(parents=True, exist_ok=True)
    with open(phase_path, "w", encoding="utf-8") as f:
        f.write(phase_props)




# Escreve o transportProperties completo na raiz para compatibilidade total com o leitor paralelo
    trans_path = case_dir / "constant" / "transportProperties"
    trans_content = f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2606                                  |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M manipulation |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      transportProperties;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

phases (water air);

sigma   0.0728;

water
{{
    transportModel  Newtonian;
    nu              {cfg.kinematic_viscosity:.7e};
    rho             1000;
}}

air
{{
    transportModel  Newtonian;
    nu              1.48e-05;
    rho             1.2;
}}

// ************************************************************************* //
"""
    with open(trans_path, "w", encoding="utf-8") as f:
        f.write(trans_content)




    # 2. Write 0/U
    u_file = f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2606                                  |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M manipulation |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       volVectorField;
    location    "0";
    object      U;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 {cfg.velocity_inlet});

boundaryField
{{
    inlet_agua
    {{
        type            fixedValue;
        value           uniform ({cfg.velocity_agua} 0 0);
    }}
    inlet_ar
    {{
        type            fixedValue;
        value           uniform ({cfg.velocity_ar} 0 0);
    }}

    outlet
    {{
        type            zeroGradient;
    }}

    walls
    {{
        type            noSlip;
    }}
}}

// ************************************************************************* //
"""
    u_path = zero_dir / "U"
    with open(u_path, "w", encoding="utf-8") as f:
        f.write(u_file)

    # 3. Write 0/p_rgh (Modified pressure for interFoam)
    p_rgh_file = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2606                                  |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M manipulation |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0";
    object      p_rgh;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [1 -1 -2 0 0 0 0];

internalField   uniform 0;

boundaryField
{
        inlet_agua
    {
        type            fixedValue;
        value           uniform 0;
    }
    inlet_ar
    {
    
        type            fixedValue;
        value           uniform 0;
    }

    outlet
    {
        type            fixedValue;
        value           uniform 0;
    }

    walls
    {
        type            fixedFluxPressure;
        value           uniform 0;
    }
}

// ************************************************************************* //
"""
    p_rgh_path = zero_dir / "p_rgh"
    with open(p_rgh_path, "w", encoding="utf-8") as f:
        f.write(p_rgh_file)

    # 4. Write 0/alpha.water
    alpha_water = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2606                                  |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M manipulation |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0";
    object      alpha.water;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 0 0 0 0 0 0];

internalField   uniform 0;

boundaryField
{
        inlet_agua
    {
        type            fixedValue;
        value           uniform 1;
    }
    inlet_ar
    {
    
        type            fixedValue;
        value           uniform 0;
    }

    outlet
    {
        type            zeroGradient;
    }

    walls
    {
        type            zeroGradient;
    }
}

// ************************************************************************* //
"""
    alpha_w_path = zero_dir / "alpha.water"
    with open(alpha_w_path, "w", encoding="utf-8") as f:
        f.write(alpha_water)

    # 5. Write 0/alpha.air
    alpha_air = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2606                                  |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M manipulation |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0";
    object      alpha.air;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 0 0 0 0 0 0];

internalField   uniform 1;

boundaryField
{
    inlet_agua
    {
        type            fixedValue;
        value           uniform 0;
    }
    inlet_ar
    {
    
        type            fixedValue;
        value           uniform 1;
    }

    outlet
    {
        type            zeroGradient;
    }

    walls
    {
        type            zeroGradient;
    }
}

// ************************************************************************* //
"""

# 6. Write 0/nut (Turbulent viscosity for kOmegaSST)
    nut_file = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2606                                  |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M manipulation |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0";
    object      nut;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -1 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    inlet_agua
    {
        type            calculated;
        value           uniform 0;
    }
    inlet_ar
    {
        type            calculated;
        value           uniform 0;
    }

    outlet
    {
        type            calculated;
        value           uniform 0;
    }

    walls
    {
        type            nutkWallFunction;
        value           uniform 0;
    }
}

// ************************************************************************* //
"""
    nut_path = zero_dir / "nut"
    with open(nut_path, "w", encoding="utf-8") as f:
        f.write(nut_file)

# 7. Write 0/k (Turbulent kinetic energy for kOmegaSST)
    k_file = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2606                                  |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M manipulation |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0";
    object      k;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0.01;

boundaryField
{
    inlet_agua
    {
        type            fixedValue;
        value           uniform 0.001;
    }
    inlet_ar
    {
        type            fixedValue;
        value           uniform 0.001;
    }

    outlet
    {
        type            zeroGradient;
    }

    walls
    {
        type            kqRWallFunction;
        value           uniform 0.01;
    }
}

// ************************************************************************* //
"""
# 8. Write 0/omega (Specific dissipation rate for kOmegaSST)
    omega_file = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2606                                  |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M manipulation |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0";
    object      omega;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 0 -1 0 0 0 0];

internalField   uniform 10;

boundaryField
{
    inlet_agua
    {
        type            fixedValue;
        value           uniform 0.01;
    }
    inlet_ar
    {
        type            fixedValue;
        value           uniform 0.01;
    }

    outlet
    {
        type            zeroGradient;
    }

    walls
    {
        type            omegaWallFunction;
        value           uniform 10;
    }
}

// ************************************************************************* //
"""
# 9. Write constant/g (Gravity vector for interFoam)
    g_path = case_dir / "constant" / "g"
    g_content = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2606                                  |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M manipulation |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       uniformDimensionedVectorField;
    location    "constant";
    object      g;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 1 -2 0 0 0 0];
value           (0 -9.81 0);

// ************************************************************************* //
"""
    with open(g_path, "w", encoding="utf-8") as f:
        f.write(g_content)

    omega_path = zero_dir / "omega"
    with open(omega_path, "w", encoding="utf-8") as f:
        f.write(omega_file)

    k_path = zero_dir / "k"
    with open(k_path, "w", encoding="utf-8") as f:
        f.write(k_file)


    alpha_a_path = zero_dir / "alpha.air"
    with open(alpha_a_path, "w", encoding="utf-8") as f:
        f.write(alpha_air)

    print("Multiphase physics boundary conditions and phaseProperties generated successfully.")

if __name__ == "__main__":
    config = SimulationConfig()
    target_case = Path("template_case")
    setup_physics_files(config, target_case)