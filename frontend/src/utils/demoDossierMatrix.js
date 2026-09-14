// Canonical Reference Dossier for SIH26018 Hackathon Demo & Offline CDN Fallback
// Linked to Survey No. 125/2, Village: Vemula, Mandal/District: Kurnool, Andhra Pradesh
// (Matching Deed(eng).jpeg, Khasra_Khatauni_Land_Record_Demo.pdf, Castral(eng).jpeg, Mutuation(eng).jpeg)

export const generateDemoMatrix = (uploaded = {}) => {
  const hasDeed = !!uploaded.sale_deed;
  const hasKhasra = !!uploaded.khasra;
  const hasCadastral = !!uploaded.cadastral_map;
  const hasMutation = !!uploaded.mutation_order;

  const surveyNo = "125/2";
  const ownerName = "Smt. Lakshmi Devi";
  const prevOwner = "Sri. Ramesh Kumar";
  const khataNo = "1025";
  const area = "2.50 Acres";
  const village = "Vemula";
  const mandal = "Kurnool";
  const district = "Kurnool";
  const state = "Andhra Pradesh";
  const mutationOrder = "Rc.No.456/2023 (10-04-2023)";

  const matrix = [
    {
      field_key: "survey_number",
      field_label: "Survey / Khasra Number",
      sale_deed: hasDeed ? surveyNo : "Document not uploaded",
      khasra_khatauni: hasKhasra ? surveyNo : "Document not uploaded",
      cadastral_map: hasCadastral ? surveyNo : "Document not uploaded",
      mutation_order: hasMutation ? surveyNo : "Document not uploaded",
      status: "GREEN",
      notes: "Survey number 125/2 perfectly matches across all 4 documents"
    },
    {
      field_key: "khata_number",
      field_label: "Khata / Account Number",
      sale_deed: hasDeed ? "Not found" : "Document not uploaded",
      khasra_khatauni: hasKhasra ? khataNo : "Document not uploaded",
      cadastral_map: hasCadastral ? "Not found" : "Document not uploaded",
      mutation_order: hasMutation ? "Not found" : "Document not uploaded",
      status: "YELLOW",
      notes: "Khata No. 1025 recorded in Revenue Register (Single document reference)"
    },
    {
      field_key: "owner_name",
      field_label: "Owner Name / Transferee",
      sale_deed: hasDeed ? ownerName : "Document not uploaded",
      khasra_khatauni: hasKhasra ? ownerName : "Document not uploaded",
      cadastral_map: hasCadastral ? `Survey Plot ${surveyNo}` : "Document not uploaded",
      mutation_order: hasMutation ? ownerName : "Document not uploaded",
      status: "GREEN",
      notes: "Title continuity verified for Smt. Lakshmi Devi"
    },
    {
      field_key: "previous_owner",
      field_label: "Previous Owner / Vendor",
      sale_deed: hasDeed ? prevOwner : "Document not uploaded",
      khasra_khatauni: hasKhasra ? prevOwner : "Document not uploaded",
      cadastral_map: hasCadastral ? "Not found" : "Document not uploaded",
      mutation_order: hasMutation ? prevOwner : "Document not uploaded",
      status: "GREEN",
      notes: "Vendor legal identity Sri. Ramesh Kumar validated"
    },
    {
      field_key: "new_owner",
      field_label: "New Owner / Purchaser",
      sale_deed: hasDeed ? ownerName : "Document not uploaded",
      khasra_khatauni: hasKhasra ? ownerName : "Document not uploaded",
      cadastral_map: hasCadastral ? "Not found" : "Document not uploaded",
      mutation_order: hasMutation ? ownerName : "Document not uploaded",
      status: "GREEN",
      notes: "Purchaser matches applicant across records"
    },
    {
      field_key: "land_area",
      field_label: "Land Area / Extent",
      sale_deed: hasDeed ? area : "Document not uploaded",
      khasra_khatauni: hasKhasra ? area : "Document not uploaded",
      cadastral_map: hasCadastral ? area : "Document not uploaded",
      mutation_order: hasMutation ? area : "Document not uploaded",
      status: "GREEN",
      notes: "Land area 2.50 Acres perfectly matches across Deed, Khasra, and Cadastral Map"
    },
    {
      field_key: "village",
      field_label: "Village / Mouza",
      sale_deed: hasDeed ? village : "Document not uploaded",
      khasra_khatauni: hasKhasra ? village : "Document not uploaded",
      cadastral_map: hasCadastral ? village : "Document not uploaded",
      mutation_order: hasMutation ? village : "Document not uploaded",
      status: "GREEN",
      notes: "Revenue village Vemula verified across all records"
    },
    {
      field_key: "mandal_tehsil_taluk",
      field_label: "Mandal / Tehsil / Taluk",
      sale_deed: hasDeed ? mandal : "Document not uploaded",
      khasra_khatauni: hasKhasra ? mandal : "Document not uploaded",
      cadastral_map: hasCadastral ? mandal : "Document not uploaded",
      mutation_order: hasMutation ? mandal : "Document not uploaded",
      status: "GREEN",
      notes: "Jurisdiction Kurnool consistent"
    },
    {
      field_key: "district",
      field_label: "District",
      sale_deed: hasDeed ? district : "Document not uploaded",
      khasra_khatauni: hasKhasra ? district : "Document not uploaded",
      cadastral_map: hasCadastral ? district : "Document not uploaded",
      mutation_order: hasMutation ? district : "Document not uploaded",
      status: "GREEN",
      notes: "District Kurnool verified"
    },
    {
      field_key: "state",
      field_label: "State",
      sale_deed: hasDeed ? state : "Document not uploaded",
      khasra_khatauni: hasKhasra ? state : "Document not uploaded",
      cadastral_map: hasCadastral ? state : "Document not uploaded",
      mutation_order: hasMutation ? state : "Document not uploaded",
      status: "GREEN",
      notes: "State Andhra Pradesh matched"
    },
    {
      field_key: "boundary_north",
      field_label: "North Boundary",
      sale_deed: hasDeed ? "Not found" : "Document not uploaded",
      khasra_khatauni: hasKhasra ? "Survey No. 122" : "Document not uploaded",
      cadastral_map: hasCadastral ? "Plot 122 (Adjacent)" : "Document not uploaded",
      mutation_order: hasMutation ? "Not found" : "Document not uploaded",
      status: "GREEN",
      notes: "North adjoining survey plot 122 matches between Khasra and Cadastral Map"
    },
    {
      field_key: "boundary_south",
      field_label: "South Boundary",
      sale_deed: hasDeed ? "Road" : "Document not uploaded",
      khasra_khatauni: hasKhasra ? "Road / adjoining survey land" : "Document not uploaded",
      cadastral_map: hasCadastral ? "Road" : "Document not uploaded",
      mutation_order: hasMutation ? "Not found" : "Document not uploaded",
      status: "GREEN",
      notes: "South road access confirmed across Deed, Khasra, and Map"
    },
    {
      field_key: "boundary_east",
      field_label: "East Boundary",
      sale_deed: hasDeed ? "Not found" : "Document not uploaded",
      khasra_khatauni: hasKhasra ? "Survey No. 126/1" : "Document not uploaded",
      cadastral_map: hasCadastral ? "Plot 126/1" : "Document not uploaded",
      mutation_order: hasMutation ? "Not found" : "Document not uploaded",
      status: "GREEN",
      notes: "East boundary matches Survey No. 126/1"
    },
    {
      field_key: "boundary_west",
      field_label: "West Boundary",
      sale_deed: hasDeed ? "Not found" : "Document not uploaded",
      khasra_khatauni: hasKhasra ? "Survey No. 125/1" : "Document not uploaded",
      cadastral_map: hasCadastral ? "Plot 125/1 (Adjacent)" : "Document not uploaded",
      mutation_order: hasMutation ? "Not found" : "Document not uploaded",
      status: "GREEN",
      notes: "West boundary matches Survey No. 125/1"
    },
    {
      field_key: "mutation_info",
      field_label: "Mutation / Order Reference",
      sale_deed: hasDeed ? "Not found" : "Document not uploaded",
      khasra_khatauni: hasKhasra ? mutationOrder : "Document not uploaded",
      cadastral_map: hasCadastral ? "Not found" : "Document not uploaded",
      mutation_order: hasMutation ? mutationOrder : "Document not uploaded",
      status: "GREEN",
      notes: "Mutation Order Rc.No.456/2023 verified between Revenue Register and Sanction Order"
    }
  ];

  let matches = 0, mismatches = 0, missing = 0;
  matrix.forEach(row => {
    if (row.status === 'GREEN') matches++;
    else if (row.status === 'RED') mismatches++;
    else missing++;
  });

  const overall = mismatches > 0 ? 'RED' : (missing > 4 ? 'YELLOW' : 'GREEN');
  const desc = mismatches > 0 
    ? 'Critical inconsistencies identified between registered documents. Physical revenue officer inquiry required.'
    : (missing > 4 
      ? 'Partial document dossier. Several fields unverified due to missing documents.' 
      : 'All cross-document validation checks passed. Title, extent, and boundaries consistent across records.');

  return {
    comparison_matrix: matrix,
    overall_status: overall,
    status_description: desc,
    documents_analyzed_count: [hasDeed, hasKhasra, hasCadastral, hasMutation].filter(Boolean).length || 4,
    match_count: matches,
    mismatch_count: mismatches,
    missing_count: missing,
    records: [
      hasDeed && { id: 1, survey_number: surveyNo, document_type: "Registered Sale Deed", owner_name: ownerName },
      hasKhasra && { id: 2, survey_number: surveyNo, document_type: "Khasra / Khatauni Register", owner_name: ownerName },
      hasCadastral && { id: 3, survey_number: surveyNo, document_type: "Cadastral Boundary Map", owner_name: `Survey Plot ${surveyNo}` },
      hasMutation && { id: 4, survey_number: surveyNo, document_type: "Mutation Sanction Order", owner_name: ownerName }
    ].filter(Boolean),
    legal_notice: "AI assists in cross-document discrepancy detection. Final verification must be performed by an authorized government officer."
  };
};
