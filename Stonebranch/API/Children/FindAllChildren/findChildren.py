import sys
import os
import pandas as pd
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from utils.stbAPI import updateAuth, updateAPIAuth, updateURI, getTaskAPI
from utils.readFile import loadJson
from utils.createFile import createExcel, createJson
from utils.readExcel import getDataExcel

from collections import OrderedDict


workflow_list = [
    #'DWH_P_FLPN_D_B',
    #'DWH_P_FLPN_M_B'
    # 'DWH_AFTER_DAILY_B',
    'DWH_MIS_ALL_DAY_B',
    # 'DWH_MIS_D01_B',
    # 'DWH_MIS_D02_B',
    # 'DWH_MIS_D03_B',
    # 'DWH_MIS_D04_B',
    # 'DWH_MIS_D05_B',
    # 'DWH_MIS_D06_B',
    # 'DWH_MIS_D07_B',
    # 'DWH_MIS_D08_B',
    # 'DWH_MIS_D09_B',
    # 'DWH_MIS_D10_B',
    # 'DWH_MIS_D11_B',
    # 'DWH_MIS_D12_B',
    # 'DWH_MIS_D13_B',
    # 'DWH_MIS_D14_B',
    # 'DWH_MIS_D15_B',
    # 'DWH_MIS_D16_B',
    # 'DWH_MIS_D17_B',
    # 'DWH_MIS_D18_B',
    # 'DWH_MIS_D20_B',
    # 'DWH_MIS_D22_B',
    # 'DWH_MIS_D24_B',
    # 'DWH_MIS_D25_B',
    # 'DWH_MIS_D26_B',
    # 'DWH_MIS_D28_B',
    # 'DWH_MONTH_END_B',
    # 'DWH_AMLO_MAIN_DAILY_B'

]

# ONICE_ONHOLD_B
# workflow_list = [
#     'DWH_ONICE_ONHOLD_B'
# ]

# All MDM
# workflow_list = [
# 'DWH_MDM_NBO_CAMPAIGN_B',
# 'DWH_MDM_OB_CIGNA_LOG_B',
# 'DWH_MDM_PRODUCT_OFFER_B',
# 'DWH_MDM_TTB_RESERVE_D_B',
# 'DWH_MDM_TTB_RESERVE_M_B',
# 'MDM_ACTIVATE_MTHLY_B',
# 'MDM_AIS_BULK_SMS_B',
# 'MDM_AL_HP_CA_INFO_DAIL_B',
# 'MDM_AL_HP_CA_INFO_MTHLY_B',
# 'MDM_AL_HP_SVG_COLLAT_B',
# 'MDM_ALDX_D_B',
# 'MDM_ALL_FREE_BENEFIT_B',
# 'MDM_ALM_PROD_PROFL_D_B',
# 'MDM_BA_FUND_CUST_I1_B',
# 'MDM_BZB_EXTRA_PT_HIST_MTHLY',
# 'MDM_BZB_PRIVLG_FLAG_M_B',
# 'MDM_CAMPAIGN_CREATION_B',
# 'MDM_CAMPAIGN_HIST_SF_B',
# 'MDM_CAR_LOYALTY_DAILY_B',
# 'MDM_CAR_LOYALTY_WEEKLY_B',
# 'MDM_CC_CMP_TRACKING_M_B',
# 'MDM_CMP_DEVIATION_WOW_B',
# 'MDM_CMP_EXP_LOYALTY.D_B',
# 'MDM_CMP_EXP_MKT_LEAD_EMAIL_B',
# 'MDM_CMP_EXP_OA_B',
# 'MDM_CMP_EXPORT3.15M_B',
# 'MDM_CMP_IMP_COM_CAMP_HIST_DEL_DAILY_B',
# 'MDM_CMP_IMP_COM_DAILY_B',
# 'MDM_CMP_IMPORT_SURVEY_B',
# 'MDM_CMP_IMPORT4.30M_B',
# 'MDM_CMP_INQ_AL_LEAD_B',
# 'MDM_CMP_MGM_C2G_REG_LEAD_B',
# 'MDM_CMP_MGM_LOYALTY.D_B',
# 'MDM_CMP_OB_ADVISORY_MASTER_05.M_B',
# 'MDM_CMP_OB_ADVISORY_MASTER_20.M_B',
# 'MDM_CMP_SCHEDULER_B',
# 'MDM_CMP_SF_BRANCH_RESP_B',
# 'MDM_CMP_SF_CUST.D_B',
# 'MDM_CMP_SMS_CC_TRAVEL_B',
# 'MDM_CMP_SMS_REG_B',
# 'MDM_CMP_SMS_SOGOOOD_B',
# 'MDM_CMP_SURVEY_LEAD_B',
# 'MDM_CONTACTHIST_DAILY_B',
# 'MDM_COR_PARTY_METRIC_M_B',
# 'MDM_CREDIT_ACCT_ADJ_M_B',
# 'MDM_CRI_BRL_MTHLY_B',
# 'MDM_CRI_MTHLY_B',
# 'MDM_CRM_ACTIVITY_TYPE_B',
# 'MDM_CRM_FLOW_DAILY_B',
# 'MDM_CUST_REQUEST_SF_WEB_B',
# 'MDM_CUSTBASE_M_B',
# 'MDM_DAILY_NEXTCAMPAIGN_B',
# 'MDM_DATALAKE_DAILY_B',
# 'MDM_DDP_DROPOFF_CONFIG_D_B',
# 'MDM_DDP_DROPOFF_LEAD_7H_D_B',
# 'MDM_DDP_DROPOFF_LEAD_INTV_D_B',
# 'MDM_DP_NO_FIXED_BONUS_M_B',
# 'MDM_DPD_PAYMENT_12M_M_B',
# 'MDM_DSS_M_B',
# 'MDM_ENOTICE_B',
# 'MDM_EOD_TCON_DWH_B',
# 'MDM_EX_CMP_HIST_B',
# 'MDM_EX_TTB_PRUDENTIAL_D_B',
# 'MDM_FINAL_MTHLY_B',
# 'MDM_FINMNL_OFSA_M_B',
# 'MDM_FL_SCS_DEFAULT_M_B',
# 'MDM_FUND_ACCOUNT_D_B',
# 'MDM_FUND_HIERACY_FEE_B',
# 'MDM_GEN_WOWID_B',
# 'MDM_GENESYS_TCON_3R_B',
# 'MDM_HP_PAY_PATTERN_B',
# 'MDM_HPAP_REFER_B',
# 'MDM_HPAP_REQ_B',
# 'MDM_HPCC_RESULT_M_B',
# 'MDM_IBS_UNITLNK_B',
# 'MDM_IDMP_ACTIVITY_D_B',
# 'MDM_IDMP_BBOS_RLOS_ACTIVITY_D_B',
# 'MDM_IMP_CMP_MF_TSP_MTH_B',
# 'MDM_IMP_CMP_TROPHY_B',
# 'MDM_INTEREST_REST_FEATURE_B',
# 'MDM_LEAD_ALLOCATE_B',
# 'MDM_LEAD_MIB_RESPONSE',
# 'MDM_LOYALTY_REDEEM_DAILY_B',
# 'MDM_MIS_BATCH_01_B',
# 'MDM_MTHLY_SPE_MKTAB_B',
# 'MDM_MYCAR_INSURANCE_D_B',
# 'MDM_NBO_CAMPAIGN_B',
# 'MDM_NBO_RULE_BASE_B',
# 'MDM_NCB_AL_M_B',
# 'MDM_NRA_HLDR_M_B',
# 'MDM_ONEAPP_D_B',
# 'MDM_P_EXPORT_DO_CYC_B',
# 'MDM_P_EXPORT_DO_FC_B',
# 'MDM_P_EXPORT_DO_FCC_B',
# 'MDM_P_EXPORT_TBROKE_AUTO_D_B',
# 'MDM_P_EXPORT_TBROKE_D_B',
# 'MDM_P_EXPORT_TBROKE_HEALTH_D_B',
# 'MDM_P_EXPORT_TCON_D_B',
# 'MDM_P_MIG_SAS_BA_M_B',
# 'MDM_P_MIG_SAS_LN_M_B',
# 'MDM_P_MIG_SAS_M_B',
# 'MDM_P_MIG_SAS_MF_M_B',
# 'MDM_P_MIG_SAS_OB_M_B',
# 'MDM_P_MIG_SAS_RATIO_M_B',
# 'MDM_P_MIG_SAS_SA_M_B',
# 'MDM_RBG_MAIN_BANK_M_B',
# 'MDM_SCS_CC_CARD_B',
# 'MDM_SCS_CC_CARD_REQUEST_B',
# 'MDM_SCS_CMP_BON_20_B',
# 'MDM_SCS_CMP_BON_B',
# 'MDM_SCS_CMP_REBON_21_B',
# 'MDM_SCS_CMP_REBON_B',
# 'MDM_SFRBG_OPPORTUNITY_B',
# 'MDM_SMS_REGISTER_D_B',
# 'MDM_SMS_SUMMARY_RESULT_AIS_B',
# 'MDM_SO_GOOD_AM_D_B',
# 'MDM_SO_GOOD_PM_D_B',
# 'MDM_SOW_M_B',
# 'MDM_STG_MTHLY_B',
# 'MDM_TEMPLATE_PRICING_CC_B',
# 'MDM_TMB_UNCONPDPA_B',
# 'MDM_TMP_COMMON_EXCLUSION_Q_B',
# 'MDM_TRANFORM_MTHLY_B',
# 'MDM_TRANSFORM_SK_D_B',
# 'MDM_TRIO_CAMPAIGN_B',
# 'MDM_TROPHY_BILL_PAYMENT_B',
# 'MDM_TRUE_BULK_SMS_B',
# 'DWH_MDM_MKTAB_B',
# 'MDM_AL_EALRY_SETTLEMENT_B',
# 'MDM_BZB_CAMP_REGIS_SMS_D_B',
# 'MDM_CMP_EXP_FULFILLMENT_B',
# 'MDM_CMP_IMP_PROSPECT.W_B',
# 'MDM_CMP_REREM_M_21_B',
# 'MDM_COM_SMS_DR_BULK_GET_B',
# 'MDM_CUST_AUM_W_B',
# 'MDM_DEBENTURE_D_B',
# 'MDM_EXP_CMP_HIST_B',
# 'MDM_HP_ADDR_CNTRC_B',
# 'MDM_IDMP_CMP_EXP_B',
# 'MDM_MASTER_Q_B',
# 'MDM_P_EX_CMP_CAM_HIST_CPHT_D_B',
# 'MDM_P_IBS_UNITLNK_INV_B',
# 'MDM_PAYROLL_BY_PASS_M_B',
# 'MDM_SCS_FC_CARD_B',
# 'MDM_STGD_OB_CIGNA_LOG_B',
# 'MDM_TROPHY_TB_PRODUCT_B',
# 'DWH_MDM_IMPORT_BDH_M_B',
# 'MDM_AL_DIGITAL_CAMPAIGN_D_B',
# 'MDM_BA_FUND_CUST_I5_B',
# 'MDM_CMP_CLEAR_DIALOG_B',
# 'MDM_CMP_IMP_LOYALTY.D_B',
# 'MDM_CMP_PA4KID_INS_CAMP_HIST.IMP_C-WF',
# 'MDM_CMP_ULDX_CC_FC_B',
# 'MDM_CRM_LEAD_INFO_B',
# 'MDM_DEL_CAMP_SF_B',
# 'MDM_EXP_AVAYA_B',
# 'MDM_GENESYS_TCON_B',
# 'MDM_IDMP_BBOS_D_B',
# 'MDM_MAP_MKTAB_MTHLY_B',
# 'MDM_ONREQUEST_B',
# 'MDM_P_IBS_UNITLNK_PLAN_DTL_B',
# 'MDM_P_PFM_M_B',
# 'MDM_SI_MF_TMB_AIP_DAILY_B',
# 'MDM_TBROKE_TBK_LIFE_B',
# 'MDM_TTBBANK_LOG_B',
# 'DWH_MDM_INS_B',
# 'MDM_AL_BASE_D_B',
# 'MDM_BRANCH_PER_B',
# 'MDM_CMP_COM_DEVIATION_DAILY_B',
# 'MDM_CMP_IMP_PROSPECT.1H_B',
# 'MDM_CMP_REM_M_B',
# 'MDM_COM_IMP_INPUT_LEAD_GET_B',
# 'MDM_CUST_PAYROLL_APPLIED_WEEKLY_B',
# 'MDM_DELETE_LEAD_B',
# 'MDM_EXP_MKT_LEAD_EMAIL_DAILY_B',
# 'MDM_HP_CLOSED_M_B',
# 'MDM_IDMP_OL_DC_D_B',
# 'MDM_MERCH_ITEM_D_B',
# 'MDM_P_EX_CMP_CR_CAM_HIST_CPT_D_B',
# 'MDM_P_IBS_UNITLNK_PLCY_DTL_B',
# 'MDM_PAYROLL_SUB_GROUP_B',
# 'MDM_SCS_FC_CARD_REQUEST_B',
# 'MDM_TBROKE_LEAD_OB_B',
# 'MDM_TTB_RESERVE_M_B',
# 'DWH_MDM_CUST_WAIVE_DOC.SET_INACT-WF',
# 'MDM_AL_CAR_TYPE_B',
# 'MDM_BDH_MODEL_RESULT_B',
# 'MDM_CMP_BRANCH_PER_B',
# 'MDM_CMP_IMP_COM_WBG_LEAD_DAILY_B',
# 'MDM_CMP_OB_UNCONTACT_B',
# 'MDM_COM_CLEAR_DIALOG_DAILY_B',
# 'MDM_CUST_PROD_HOLD_DIM_DAILY_B',
# 'MDM_DEL_DLG_PARTICIPANT_B',
# 'MDM_EXP_CMP_LITE_B',
# 'MDM_HP_CA_PMT_TRAN_B',
# 'MDM_IDMP_RLOS_D_B',
# 'MDM_MF_FUND_CUST_B',
# 'MDM_P_EXPORT_DO_C2G_B',
# 'MDM_P_IBS_UNITLNK_TRAN_B',
# 'MDM_PMTPY_INFO_M_B',
# 'MDM_SILVER_CARD_MTHLY_B',
# 'MDM_TF_CSHBCK_EXP_ITFV_B',
# 'MDM_USSD_REGISTER_D_B',
# 'DWH_MDM_MF_B',
# 'MDM_AL_CYC_NEW_INT_MASTER_B',
# 'MDM_BUBK_PRICE_M_B',
# 'MDM_CMP_EXP_LEAD_CRM_B',
# 'MDM_CMP_IMPORT3.15M_B',
# 'MDM_CMP_REREM_M_B',
# 'MDM_COMPID_DRCR_B',
# 'MDM_CUST_PROFILE_CRI_RBG_B',
# 'MDM_DLM_DAILY_B',
# 'MDM_EXPORT_TO_CHUBB_B',
# 'MDM_HP_NONHP_RELIEF_M_B',
# 'MDM_IMP_CMP_LEAD_SMS_AL_B',
# 'MDM_MTHLY_CMP_D20_B',
# 'MDM_P_EXPORT_DO_CCC_B',
# 'MDM_P_IM_CAMPAIGN_FULFILLMENT_Q_B',
# 'MDM_PRE_SCORE_B',
# 'MDM_SI_MF_TMB_AIP_MTHLY_B',
# 'MDM_TEMPLATE_PRICING_FC_B',
# 'MDM_ULDX_LEAD_B',
# 'DWH_MDM_CCC_SPEEDUP_D_B',
# 'MDM_AIS_SMS_REGISTER_DAILY_B',
# 'MDM_BA_FUND_CUST_I2_B',
# 'MDM_CMP_ALCRM_ENOTI_B',
# 'MDM_CMP_IMP_COM_PROSPECT_DAILY_B',
# 'MDM_CMP_OB_CIGNA_LOG_D_B',
# 'MDM_COM_REWARD_REDEMPTION_B',
# 'MDM_CUST_OCC_SEGMENT_M_B',
# 'MDM_DEVICE_MGMT_ONEAPP_B',
# 'MDM_EXPORT_GENESYS_B',
# 'MDM_HP_CYB_AC_INFO_D_B',
# 'MDM_IDMP_SCHEDULER_B',
# 'MDM_MTHLY_CMP_MKTAB_B',
# 'MDM_P_EXPORT_DO_CYH_B',
# 'MDM_P_MIG_SAS_CC_M_B',
# 'MDM_REVENUE_FEE_M_B',
# 'MDM_SMS_COVID_B',
# 'MDM_TF_CSHBCK_IMP_LEAD_B',
# 'MDM_WLTH_FLAG_MTHLY_B',
# 'DWH_MDM_CUST_WAIVE_DOC_M_B.INACTIVE_C-WF',
# 'MDM_AL_BILL_PAYMENT_B',
# 'MDM_BIZ_ONE_SMART_SHOP_D_B',
# 'MDM_CMP_CC_SPEND_CATE_SUGG_B',
# 'MDM_CMP_IMP_EMAIL_STATUS_B',
# 'MDM_CMP_REM_M_20_B',
# 'MDM_CMP_USSD_REG_B',
# 'MDM_CRM_PAY_INFO_D_B',
# 'MDM_DDP_DROPOFF_LEAD_D_B',
# 'MDM_EX_CMP_HIST_CR_B',
# 'MDM_HOMELOAN_D_B',
# 'MDM_IDMP_CMP_EXP_D_B',
# 'MDM_MKTAB_MTHLY_B',
# 'MDM_P_EXPORT_DO_CC_B',
# 'MDM_P_MIG_SAS_BHV_M_B',
# 'MDM_PRODUCT_DIM_MTHLY_B',
# 'MDM_SMART_Q_B',
# 'MDM_TF_CSHBCK_IMP_ITFV_B',
# 'MDM_ZACC_AL_M_B'
# ]

# All OFSA
# workflow_list = [
# 'OFS_ADJUST_ALLACCT_P2_REQ_M_B',
# 'OFS_GL_PP_RECON_M_B',
# 'OFS_LOAD_FSI_INSTRUMENT_M_B',
# 'OFS_LOAD_INST_NO_I9RESULT_M_B',
# 'OFS_OUTB_INST_R2_B',
# 'OFS_PDPA_PURGE_D27_M_B',
# 'OFS_PRELIM_LOAD_ALLACC_R2_B',
# 'OFS_PRELIM_R2_B',
# 'OFS_RPT_MTHLY_B',
# 'OFS_ADJUST_ALL_ACCOUNT_REQ_M_B',
# 'OFS_LOAD_ALL_ACC_M_B',
# 'OFS_LOAD_FTP_DATA_M_B',
# 'OFS_LOAD_MGT_LEDGER_M_B',
# 'OFS_OUTB_RPT_ALLACCT_ADJ_B',
# 'OFS_PFT_PREP_M_B',
# 'OFS_PRELIM_LOAD_GL_DATA_M_B',
# 'OFS_RPT_BGT_LOAD_FACT_B',
# 'OFS_RPT_PRELIM_B',
# 'OFS_ADHOC_MGT_VERSION_B',
# 'OFS_FTP_RULES_M_B',
# 'OFS_LOAD_EXCH_RATE_P_B',
# 'OFS_LOAD_SPECAIL_ASSET_M_B',
# 'OFS_OUTB_RPT_ALLACCT_B',
# 'OFS_PFT_RULES_M_B',
# 'OFS_PRELIM_LOAD_INST_I9RESULT_M_B',
# 'OFS_RPT_BUDGET_ADHOC_B',
# 'OFS_RPT_PRELIM_GENERAL_B',
# 'OFS_DIM_PRODUCT_D_B',
# 'OFS_LOAD_DIM_M_B',
# 'OFS_LOAD_GL_DIM_M_B',
# 'OFS_NONINSTR_REPOP_M_B',
# 'OFS_OUTB_RPT_MGT_LEDGER_B',
# 'OFS_PRELIM_B',
# 'OFS_PRELIM_LOAD_INST_NO_I9RESULT_M_B',
# 'OFS_RPT_M_LOAD_FACT_B',
# 'OFS_RPT_PRELIM_GENERAL_R2_B',
# 'OFS_FEE_ALLOC_M_B',
# 'OFS_LOAD_DIM_P_B',
# 'OFS_LOAD_GL_DATA_M_B',
# 'OFS_MTHLY_MAIN_B',
# 'OFS_OUTB_RPT_PRELIM_B',
# 'OFS_PRELIM_GENERAL_B',
# 'OFS_PRELIM_LOAD_INSTRUMENT_M_B',
# 'OFS_RPT_MGT_LEDGER_M_GENERAL_B',
# 'OFS_RPT_PRELIM_LOAD_FACT_B',
# 'OFS_ALL_ACC_ADJUST_M_B',
# 'OFS_GL_RECON_CORGL2_M_B',
# 'OFS_LOAD_INST_I9RESULT_M_B',
# 'OFS_OUTB_INST_R1_B',
# 'OFS_OUTB_RPT_R2_B',
# 'OFS_PRELIM_LOAD_ALLACC_M_B',
# 'OFS_PRELIM_LOAD_SPCL_AST_M_B',
# 'OFS_RPT_MGT_LEDGER_M_LOAD_FACT_B',
# 'OFS_RPT_PRELIM_LOAD_FACT_R2_B',
# 'OFS_ADHOC_BUDGET_ALLOC_B',
# 'OFS_GL_RECON_1_M_B',
# 'OFS_LOAD_FSI_I9RESULT_M_B',
# 'OFS_MTHLY_GENERAL_B',
# 'OFS_OUTB_RPT_R1_B',
# 'OFS_PRELIM_GL_PP_RECON_NONINSTR_M_B',
# 'OFS_PRELIM_LOAD_MGT_LDG_M_B',
# 'OFS_RPT_MGT_LEDGER_MTHLY_B',
# 'OFS_RPT_PRELIM_R2_B',
# 'OFS_ALL_ACC_ADJUST_REQ_M_B',
# 'OFS_HKP_GATHER_SCHEMA_M_B',
# 'OFS_LOAD_FSI_NO_I9RESULT_M_B',
# 'OFS_LOAD_INSTRUMENT_DATA_M_B',
# 'OFS_OUTB_RPT_ADHOC_BGT_B',
# 'OFS_PFT_DRIVER_TXN_LOAD_M_B',
# 'OFS_PRELIM_LOAD_FSI_INSTRU_M_B',
# 'OFS_RPT_BGT_ADHOC_GENERAL_B',
# 'OFS_RPT_MTHLY_GENERAL_B',
# 'OFS_RPT_SET_STATUS_REQ_B'
# ]



# DWH-TRIGGER
# workflow_list = [
#     'DWH_DAILY_BATCH_TRIG1_B',
#     'DWH_DAILY_BATCH_TRIG2_B',
#     'DWH_DAILY_BATCH_TRIG3_B',
#     'DWH_DAILY_BATCH_TRIG4_B',
#     'DWH_DAILY_BATCH_TRIG5_B',
#     'DWH_DAILY_BATCH_TRIG6_B'
# ]

# LON Class & RDT
# workflow_list = [
#     'DI_DWH_LCS_S.CHK_DATA_B',
#     'DI_DWH_LON_CLASS_B',
#     'DWH_LCS_W.CHK_DATA_B',
#     #'DWH_LON_CLASS_WEEKLY_B',
#     'DWH_RDT_ACS_PREP_M_B',
#     'DWH_RDT_BU_MATRIX_Q_B',
#     'DWH_RDT_DAILY_B',
#     'DWH_RDT_G1_MTHLY_B',
#     'DWH_RDT_G2_MTHLY_B',
#     'DWH_RDT_INBOUND_D_B',
#     'DWH_RDT_INBOUND_M_B',
#     'DWH_RDT_ONETIME_M_B'
# ]
    

# OFSA
# workflow_list = [
#     'OFS_RPT_PREP_D1_M_B',
#     'OFS_RPT_PREP_D8_M_B',
#     'OFS_RPT_PREP_D9_M_B',
#     'OFS_RPT_PREP_D10_M_B',
#     'OFS_RPT_PREP_D13_M_B',
#     'OFS_SQLQUERY_REQ_B',
#     'OFS_SCD_GL_DIM_REQ_M_B',
#     'OFS_LOAD_TB_DATA_REQ_M_B',
#     'OFS_HKP_MTHLY_B',
#     'OFS_HKP_YEARLY_B',
#     'OFS_ADHOC_LDAP_B',
# ]


# Non HP & HP Loan Class
# workflow_list = [
#     'DWH_REGULATORY_B',
#     'DWH_LCS_TRIGGER_B',
#     'DI_DWH_LON_CLASS_B',
#     'DWH_XREF_BOT_SOFTLOAN_M_B',
#     'DWH_LON_WRITEOFF_MTHLY_B',
#     'DWH_LON_CLASS_B_NOTI_FIN_B',
#     'DWH_FI_LOAN_CLASS',
#     'DWH_BOT_REL_MTHLY_B',
#     'DWH_SBO_ACCT_B',
#     'DWH_LON_CLASS_NOTIFY_FIN_B',
#     'DWH_LCR.D.02.LCR_CUST_RELATION_B',
#     'DWH_EX_ROS_DWH_EDD_M_B',
#     'DWH_SC_CUST_PROFILE_M_B',
#     'DWH_RPT_LCS_B',
#     'DWH_OFSAA_CL_M.M.UPD_AVG_C',
#     'DWH_AR_TCG_ADJ_B',
#     'DWH_CHK_LCS.TRIG_C'
# ]

# Non HP & HP Stage Migration
# workflow_list = [
#     'DWH_MNL_STAGE_MIG_HP_M_B',
#     'DWH_STAGE_MIGRT_M_HP_B',
#     'DWH_STAGE_MIGRT_ONREQUEST_B',
#     'DWH_MNL_STAGE_MIG_M_B'
# ]

# Non HP & HP Outbound
# workflow_list = [
#     'DWH_CRI_INB_M_B',
#     'DWH_IFRS9_REG_M_B',
#     'DWH_IFRS9_HP_TRIGGER_M_B',
#     'DWH_P_B_SCORE_M_B',
#     'DWH_IFRS9_MONTHLY_B',
#     'DWH_STAGE_MIGRT_M_HP_B.INACT_C',
#     'DWH_IFRS9_MONTHLY.INACT_C',
#     'DWH_IFRS9_BACKUP_M_B',
#     'DWH_IFRS9_MONTHLY_B.SUCCESS_C',
#     'DWH_IFRS9_DAILY_MAIL_B',
#     'DWH_LON_PAMCO_I9_M_B',
#     'DWH_IFRS9_B_SCORE_M.INACT_C'
# ]

# Non HP & HP Inbound
# workflow_list = [
#     'DWH_IFRS9_TRIG_NON_HP_B',
#     'DWH_IFRS9_INBOUND_M_B',
#     'DWH_IFRS9_INBOUND_M_B.SUCCESS_C',
#     'DWH_FEE_TXN_MTHLY_ADJ_B',
#     'DWH_IAS_ADJ_INT_MTH_B',
#     'DWH_PBI_FINANCE_RERUN_B',
#     'DWH_IFRS9_TRIGGER.OSX_SUCCESS_SPOOL_C',
#     'DWH_IFRS9_TRIGGER.OSX_SUCCESS_FTP_C',
#     'DWH_TFRS9_MONTHLY_PL_BY_ACCOUNT_B',
#     'DWH_P_TX_RE_APPRISAL_M_B',
#     'DWH_IFRS9_CONSOLIDATE_B.ON_HOLD_C',
#     'DWH_IFRS9_INBOUND_M_B.ON_HOLD_C',
#     'DWH_IFRS9_HP_INBOUND_M_B.ON_HOLD_C',
#     'DWH_IFRS9_TRIG_NON_HP_ADJ_B',
#     'DWH_IFRS9_INBOUND_D7_B',
#     'DWH_IFRS9_INBOUND_D7_B.FINISH_MAIL_C',
#     'DWH_OFS_OUT_02_MTHLY_B',
#     'DWH_IFRS9_INBOUND_D7_B_SUCCESS_ST_C',
#     'DWH_IFRS9_TRIG_HP_B',
#     'DWH_IFRS9_HP_INBOUND_M_B',
#     'DWH_MNL_OTH_AST_B',
#     'DWH_IFRS9_UPD_ZACC_B',
#     'DWH_IFRS9_CONSOLIDATE_B',
#     'DWH_REG_ZACCHIST_B',
#     'DWH_P_TX_AL_RPT_M_B'
# ]

# Non HP & HP Manual File
# workflow_list = [
#     'DWH_LEASING_MTHLY_B',
#     'DWH_P_KYC_PROD_HLD_MTHLY_B',
#     'DWH_AL_ADJ_AMT_MTHLY_B',
#     'DWH_RM_CSM_MTHLY_B',
#     'DWH_LON_HAIR_CUT_B',
#     'DWH_MNL_BOT_SKIP_PAY_B',
#     'DWH_POST_RLF_M_B',
#     'DWH_POST_RLF_CMCL_CV99_M_B',
#     'DWH_POST_RLF_CMCL_CV99_M_B.INACTIVE_C',
#     'DWH_OMS_LOAD_LO_TDR_B'
# ]

# DWH-RDT
# workflow_list = [
#     'DWH_RDT_DAILY_B',
#     'DWH_RDT_ACS_PREP_M_B',
#     'DWH_RDT_G1_MTHLY_B',
#     'DWH_RDT_G2_MTHLY_B',
#     'DWH_RDT_MONTHLY_CLR_C',
#     'DWH_RDT_ONETIME_M_B',
#     'DWH_RDT_BU_MATRIX_Q_B',
#     'DWH_RDT_INBOUND_M_B',
#     'DWH_RDT_INBOUND_D_B'
# ]

# RDT-DQ
# workflow_list = [
#     'DWH_RDT_DQ_PRG_MANUAL_B',
#     'DWH_RDT_DQ_DAILY_D_B',
#     'DWH_RDT_DQ_MTHLY_G1_M_B',
#     'DWH_RDT_DQ_MTHLY_G2_M_B'
# ]

# DWH-interval
# workflow_list = [
#     'DWH_ATM_TX_B',
#     'DWH_AML_THLIST_CUST_B',
#     'DWH_AML_THLIST_CUST_VT_SRC_B',
#     'DWH_AML_THLIST_CUST_FLG_B',
#     'DWH_CC_OASLOG.5M_B',
#     'DWH_P_MONITOR_B',
#     'DWH_EXIM_IBO_TIMING_B',
#     'CPIC_CPL_DAILY_B',
#     'CPIC_DAILY_B',
#     'CPIC_FRAUD_DAILY_B',
#     'DWH_OMS_DS_DEP_AVG_DAILY_B',
#     'DWH_OMS_PA_POPULATE_DETAIL_LEAVES_D_B',
#     'MQM_CIDM_DAILY_B',
#     'CPIC_FRAUD.1_B',
#     'CPIC_FRAUD.2_B',
#     'CPIC_FRAUD.3_B',
#     'CPIC_FRAUD.4_B',
#     'CPIC_FRAUD_EXP.DELTA_B',
#     'DWH_CPIC_FRAUD_B',
#     'DWH_OMS_LOAD_FX_OTHTXN_MAN_B',
#     'DWH_OMS_LOAD_FX_TXN_FCD_V2_B',
#     'DWH_OMS_LOAD_NR_TRANS_B',
#     'DWH_OMS_UPD_LOAN_BUS_TXT_LOAD_B',
#     'DWH_TPFM_PROC_BRN_LST_B',
#     'DWH_RMI_BLS.D_B',
#     'DWH_OMS_DS_LTV_B',
# ]

# DWH-interval 2
# workflow_list = [
#     'CPIC_CPL_DAILY_B',
#     'CPIC_DAILY_B',
#     'CPIC_FRAUD.1_B',
#     'CPIC_FRAUD.2_B',
#     'CPIC_FRAUD.3_B',
#     'CPIC_FRAUD.4_B',
#     'CPIC_FRAUD_DAILY_B',
#     'CPIC_FRAUD_EXP.DELTA_B',
#     'DWH_AML_THLIST_CUST_B',
#     'DWH_AML_THLIST_CUST_FLG_B',
#     'DWH_AML_THLIST_CUST_VT_SRC_B',
#     'DWH_ATM_TX_B',
#     'DWH_CC_OASLOG.5M_B',
#     'DWH_CPIC_FRAUD_B',
#     'DWH_EXIM_IBO_TIMING_B',
#     'DWH_OMS_DS_DEP_AVG_DAILY_B',
#     'DWH_OMS_DS_LTV_B',
#     'DWH_OMS_LOAD_FX_OTHTXN_MAN_B',
#     'DWH_OMS_LOAD_FX_TXN_FCD_V2_B',
#     'DWH_OMS_LOAD_NR_TRANS_B',
#     'DWH_OMS_PA_POPULATE_DETAIL_LEAVES_D_B',
#     'DWH_OMS_UPD_LOAN_BUS_TXT_LOAD_B',
#     'DWH_OMS_WSHEET_UPD_RPT_BOT_CONSUMER_B',
#     'DWH_P_MONITOR_B',
#     'DWH_RMI_BLS.D_B',
#     'DWH_TPFM_PROC_BRN_LST_B',
#     'MQM_CIDM_DAILY_B',
# ]

TOPIC_COLUMN = "jobName"


CHILDREN_FIELD = "Children"
CHILD_TYPE = "Task Type"
CHILD_LEVEL = "Task Level"
WORKFLOW_NAME = "Workflow"
NEXT_NODE = "Next Node"
PREVIOUS_NODE = "Previous Node"
BUSNESS_SERVICE = "Business Service"

EXTRA_1 = "Execution Restriction"
EXTRA_2 = "Late Finish"
EXTRA_3 = "Late Finish Duration"
EXTRA_4 = "Actions"


MAIN_WORKFLOW = "Main Workflow"


EXCEL_OUTPUT_NAME = "ChildrenExcel\\All Children In XXXXX.xlsx"


task_configs_temp = {
    'taskname': None,
}

#########################################     find children    ################################################

def findChildren(task_name, next_node=None, previous_node=None, level=0, workflow_name=None):
    if workflow_name is None:
        workflow_name = MAIN_WORKFLOW
    if next_node is None:
        next_node = []
    if previous_node is None:
        previous_node = []
    children = {}
    task_configs = task_configs_temp.copy()
    task_configs['taskname'] = task_name
    response = getTaskAPI(task_configs)
    if response.status_code == 200:
        children = {CHILD_TYPE: None, 
                    BUSNESS_SERVICE: None, 
                    CHILD_LEVEL: level, 
                    WORKFLOW_NAME:None,
                    EXTRA_1: None,
                    EXTRA_2: None,
                    EXTRA_3: None,
                    EXTRA_4: None,
                    CHILDREN_FIELD: OrderedDict(), 
                    NEXT_NODE: None, 
                    PREVIOUS_NODE: None}
        task_data = response.json()
        children[CHILD_TYPE] = task_data['type']
        children[WORKFLOW_NAME] = workflow_name
        
        children[EXTRA_1] = task_data['executionRestriction']
        children[EXTRA_2] = task_data['lfEnabled']
        children[EXTRA_3] = task_data['lfDuration']
        children[EXTRA_4] = task_data['actions'] if task_data['actions'] else None
        
        children[BUSNESS_SERVICE] = ", ".join(task_data["opswiseGroups"])
        if task_data['type'] == "taskWorkflow":
            for child in task_data['workflowVertices']:
                child_name = child['task']['value']
                child_next_node = findNextNode(child_name, task_data['workflowEdges'])
                child_previous_node = findPreviousNode(child_name, task_data['workflowEdges'])
                children["Children"][child_name] = findChildren(child_name, child_next_node, child_previous_node, level + 1, task_name)
                
        if len(next_node) > 0:
            children[NEXT_NODE] = next_node
        else:
            children[NEXT_NODE] = []
            
        if len(previous_node) > 0:
            children[PREVIOUS_NODE] = previous_node
        else:
            children[PREVIOUS_NODE] = []
    
    return children

def findNextNode(task_name, workflowEdges):
    next_node = []
    for edge in workflowEdges:
        if edge['sourceId']['taskName'] == task_name:
            next_node.append(f"{edge['targetId']['taskName']} ({edge['condition']['value']})")
    return next_node

def findPreviousNode(task_name, workflowEdges):
    previous_node = []
    for edge in workflowEdges:
        if edge['targetId']['taskName'] == task_name:
            previous_node.append(f"{edge['sourceId']['taskName']} ({edge['condition']['value']})")
    return previous_node

def countChildren(children_dict):
    count = 0
    for child_name, child_data in children_dict["Children"].items():
        count += 1  # Count this child
        count += countChildren(child_data)  # Recursively count the child's children
    return count

############################################################################################################

def searchAllChildrenInWorkflow(workflow_list):
    all_children_dict = {}
    for workflow_name in workflow_list:
        print(f"Searching children of {workflow_name}")
        all_children_dict[workflow_name] = findChildren(workflow_name)
        total_children = countChildren(all_children_dict[workflow_name])
        print(f"Total children: {total_children}")
    return all_children_dict


############################################################################################################

# def prepareChildrenList(children_json, parent_name, children_list):
#     if children_json["Children"]:
#         for childname, child_data in children_json["Children"].items():
#             child_level = child_data["Child Level"]
#             child_type = child_data["Child Type"]
#             next_node = child_data["Next Node"]
#             if next_node == []:
#                 next_node = None
#             children_list.append({
#                 'Taskname': childname,
#                 'workflow': parent_name,
#                 'Child Level': child_level,
#                 'Child Type': child_type,
#                 'Next Node': next_node
#             })
#             if child_data["Children"]:
#                 children_list = prepareChildrenList(child_data, childname, children_list)
#     return children_list


# def prepareChildrenListAllLevel(children_dict):
#     df_all_children_list = {}
#     for workflow_name, children_dict in children_dict.items():
#         children_list = prepareChildrenList(children_dict, workflow_name, children_list)
        
#         df_children_list = pd.DataFrame(children_list)
#         df_all_children_list[workflow_name] = df_children_list
#     return df_all_children_list

def flattenChildrenHierarchy(children_json, parent_path=None):
    if parent_path is None:
        parent_path = []

    rows = []
    if children_json["Task Level"] == 0:
        rows.append({
            "Path": parent_path,
            "Business Service": children_json[BUSNESS_SERVICE],
            "Taskname": None,
            "Workflow": children_json[WORKFLOW_NAME],
            "Task Level": children_json[CHILD_LEVEL],
            "Task Type": children_json[CHILD_TYPE],
            "Execution Restriction": children_json[EXTRA_1],
            "Late Finish": children_json[EXTRA_2],
            "Late Finish Duration": children_json[EXTRA_3],
            "Actions": children_json[EXTRA_4],
            "Previous Node": None,
            "Next Node": None
        })
    for child_name, child_data in children_json["Children"].items():
        current_path = parent_path + [child_name]
        child_workflow_name = child_data[WORKFLOW_NAME]
        child_business_service = child_data[BUSNESS_SERVICE]
        child_level = child_data[CHILD_LEVEL]
        child_type = child_data["Task Type"]
        next_node = " // ".join(child_data["Next Node"]) if child_data["Next Node"] else None
        previous_node = " // ".join(child_data["Previous Node"]) if child_data["Previous Node"] else None
        execution_restriction = child_data[EXTRA_1]
        late_finish = child_data[EXTRA_2]
        late_finish_duration = child_data[EXTRA_3]
        actions = child_data[EXTRA_4]
        rows.append({
            "Path": current_path,
            "Taskname": child_name,
            WORKFLOW_NAME: child_workflow_name,
            BUSNESS_SERVICE: child_business_service,
            CHILD_LEVEL: child_level,
            CHILD_TYPE: child_type,
            EXTRA_1: execution_restriction,
            EXTRA_2: late_finish,
            EXTRA_3: late_finish_duration,
            EXTRA_4: actions,
            PREVIOUS_NODE: previous_node,
            NEXT_NODE: next_node
        })
        if child_data["Children"]:
            rows.extend(flattenChildrenHierarchy(child_data, current_path))
    return rows

def listChildrenHierarchyToDataFrameAllInOne(children_dict):
    workflow_children_dict = {}
    df_children_list = []
    max_depth = 0
    for workflow_name, workflow_children in children_dict.items():
        flattened_rows = flattenChildrenHierarchy(workflow_children)
        workflow_children_dict[workflow_name] = flattened_rows
        if flattened_rows:
            max_depth = max(max_depth, max(len(row["Path"]) for row in flattened_rows))
        
    columns = ["Business Service", "Taskname", "Task Type", "Task Level", "Execution Restriction", "Late Finish", "Late Finish Duration", "Actions", "Workflow", "Main Workflow"] + [f"Sub Level {i+1}" for i in range(max_depth)] + ["Previous Task", "Next Task"]
    
    for workflow_name, workflow_rows in workflow_children_dict.items():
        for row in workflow_rows:
            padded_path = row["Path"] + [""] * (max_depth - len(row["Path"]))
            if row[CHILD_LEVEL] == 0:
                df_children_list.append([row[BUSNESS_SERVICE], workflow_name, row[CHILD_TYPE], row[CHILD_LEVEL], row[EXTRA_1], row[EXTRA_2], row[EXTRA_3], row[EXTRA_4], row[WORKFLOW_NAME], workflow_name] + padded_path + [row[PREVIOUS_NODE], row[NEXT_NODE]])
            else:
                df_children_list.append([row[BUSNESS_SERVICE], row["Taskname"], row[CHILD_TYPE], row[CHILD_LEVEL], row[EXTRA_1], row[EXTRA_2], row[EXTRA_3], row[EXTRA_4], row[WORKFLOW_NAME], workflow_name] + padded_path + [row[PREVIOUS_NODE], row[NEXT_NODE]])
            #print(json.dumps(data, indent=10))
    df_children_list = pd.DataFrame(df_children_list, columns=columns)

    return df_children_list

# def listChildrenHierarchyToDataFrameSeparate(children_dict):
#     workflow_children_dict = {}
#     df_children_list = []
#     max_depth = 0
#     for workflow_name, workflow_children in children_dict.items():
#         flattened_rows = flattenChildrenHierarchy(workflow_children)
#         workflow_children_dict[workflow_name] = flattened_rows
#         max_depth = max(max_depth, max(len(row["Path"]) for row in flattened_rows))
        
#     columns = ["Taskname", "Task Type", "Task Level", "Main Workflow"] + [f"Sub Level {i+1}" for i in range(max_depth)] + ["Previous Task", "Next Task"]
    
#     for workflow_name, workflow_rows in workflow_children_dict.items():
#         for row in workflow_rows:
#             padded_path = row["Path"] + [""] * (max_depth - len(row["Path"]))
#             df_children_list.append([row["Taskname"], row["Task Type"], row["Task Level"], workflow_name] + padded_path + [row["Previous Node"], row["Next Node"]])
#             #print(json.dumps(data, indent=10))
#     df_children_list = pd.DataFrame(df_children_list, columns=columns)

#     return df_children_list


############################################################################################################


def main():
    auth = loadJson('auth.json')
    #userpass = auth['ASKME_STB']
    #userpass = auth['TTB_PROD']
    userpass = auth['TTB']
    updateAuth(userpass["USERNAME"], userpass["PASSWORD"])
    #updateAPIAuth(userpass["API_KEY"])
    domain_url = loadJson('Domain.json')
    #domain = domain_url['TTB_PROD']
    domain = domain_url['TTB_UAT']
    #domain = domain_url['1.173']
    updateURI(domain)
    
    df_job_list = getDataExcel("Get Excel Job List")
    workflow_list = df_job_list[TOPIC_COLUMN].tolist()
    print(f"Total workflows: {len(workflow_list)}")
    print("Finding all children of the workflow")
    all_children_dict = searchAllChildrenInWorkflow(workflow_list)
    #print(json.dumps(all_children_dict, indent=10))
    createJson("Deep\\All Children.json", all_children_dict, False)
    print("Preparing the children list")
    
    df_workflow_children_list = listChildrenHierarchyToDataFrameAllInOne(all_children_dict)
    #print(df_workflow_children_list)
    createExcel(EXCEL_OUTPUT_NAME, ("All Children",df_workflow_children_list))
    

if __name__ == "__main__":
    main()