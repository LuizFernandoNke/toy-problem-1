from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
CASE_DIR = ROOT_DIR / "template_case"

def setup_set_fields(case_dir: Path):
    """Gera o arquivo system/setFieldsDict para inicializar o padrão estratificado."""
    content = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  2606                                  |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M manipulation |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      setFieldsDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

defaultFieldValues
{
    volScalarFieldInternal
    {
        alpha.water 0;
        alpha.air   1;
    }
}

regions
{
    boxToCell
    {
        box ({-R} {-R} 0) ({R} {0.7 * cfg.diameter - R} {L})
        fieldValues
        {
            alpha.water 1;
            alpha.air   0;
        }
    }
}

// ************************************************************************* //
"""
    system_dir = case_dir / "system"
    system_dir.mkdir(parents=True, exist_ok=True)
    with open(system_dir / "setFieldsDict", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    setup_set_fields(CASE_DIR)
    print("setFieldsDict generated successfully.")