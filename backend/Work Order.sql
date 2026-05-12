-
-- Voir TOUS les jobs Released de l'org 1731 (BXD)
SELECT 
    wen.WIP_ENTITY_NAME     AS num_job,
    ite.SEGMENT1            AS item_code,
    ite.DESCRIPTION         AS description,
    wdj.STATUS_TYPE         AS statut,
    wdj.SCHEDULED_QUANTITY  AS qty,
    wdj.SCHEDULED_COMPLETION_DATE AS date_besoin,
    wdj.CREATION_DATE       AS date_creation

FROM 
    apps.WIP_DISCRETE_JOBS   wdj,
    apps.WIP_ENTITIES        wen,
    apps.MTL_SYSTEM_ITEMS_B  ite

WHERE 
    wdj.WIP_ENTITY_ID   = wen.WIP_ENTITY_ID
    AND wdj.PRIMARY_ITEM_ID = ite.INVENTORY_ITEM_ID
    AND wdj.ORGANIZATION_ID = ite.ORGANIZATION_ID
    AND wdj.STATUS_TYPE     = 3        -- ← Released
    AND wdj.ORGANIZATION_ID = '1731'   -- ← BXD
    AND wdj.CREATION_DATE   > SYSDATE - 90  -- ← 3 mois

ORDER BY 
    wdj.SCHEDULED_COMPLETION_DATE ASC
;


Connection name
	
gltest


Username
	
SSO


Password
	
 


Hostname
	
qahceaexa-scan.ge-healthcare.net


Port
	
1521


Choose Service name


Service name
	
ebs_gltest