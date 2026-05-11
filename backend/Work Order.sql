-- Work Order
-- Find job from assembly, op, organization
SELECT 	ite.SEGMENT1		ASSEMBLY,       
		ood.ORGANIZATION_CODE	ORG,  
		wen.wip_entity_id,
		ite.DESCRIPTION		ASSEMBLY_DESCRIPTION, 
		DECODE(wdj.STATUS_TYPE,1,'Unreleased',3,'Released',6,'On Hold', 4, 'Completed', 7, 'Cancelled', 12, 'Closed', wdj.STATUS_TYPE )		STATUS, 
		wen.WIP_ENTITY_NAME	NUM_JOB,
		wdj.CREATION_DATE	CREATION_DATE,
        (opr.QUANTITY_IN_QUEUE + opr.QUANTITY_WAITING_TO_MOVE) AVAILABLE, 
        SCHEDULED_QUANTITY,
		(CASE WHEN opr.quantity_in_queue >=1  THEN OPERATION_SEQ_NUM
			else  opr.NEXT_OPERATION_SEQ_NUM  END) NEXT_O,
		(CASE WHEN opr.quantity_in_queue >=1  THEN 'IN_QUEUE'
			else  cast(opr.OPERATION_SEQ_NUM as varchar2(15) ) END) as OPERATION
FROM    	apps.WIP_DISCRETE_JOBS	wdj,			
			apps.WIP_ENTITIES	wen,
			apps.MTL_PARAMETERS	ood, 
			apps.MTL_SYSTEM_ITEMS_B	ite ,
			apps.wip_operations 
opr
WHERE		wdj.WIP_ENTITY_ID = wen.WIP_ENTITY_ID 
AND 		wdj.PRIMARY_ITEM_ID = ite.INVENTORY_ITEM_ID 
AND			wdj.ORGANIZATION_ID = ite.ORGANIZATION_ID 
AND			ood.ORGANIZATION_ID = wdj.ORGANIZATION_ID 
AND			WEN.WIP_ENTITY_ID = OPR.WIP_ENTITY_ID
AND     (( OPR.QUANTITY_WAITING_TO_MOVE <> 0
          	AND opr.NEXT_OPERATION_SEQ_NUM in ('10'))
              OR (OPR.QUANTITY_IN_QUEUE >= 1
				AND OPR.PREVIOUS_OPERATION_SEQ_NUM IS NULL AND OPR.OPERATION_SEQ_NUM IN ('10'))
        )
AND 		WDJ.ORGANIZATION_ID LIKE '1731'
AND ITE.SEGMENT1 IN ('5653880')
AND 		wdj.STATUS_TYPE = 3
AND 		( wdj.CREATION_DATE > sysdate - 200 
						OR 
	 	   WDJ.DATE_COMPLETED > SYSDATE - 200) 
ORDER BY WDJ.CREATION_DATE , TO_CHAR(WDJ.CREATION_DATE, 'HH24:MI:SS') ASC
;

-- Work Order
-- Find Pick list from a job and op
SELECT distinct             
                           b.SEGMENT1 ASSEMBLY,
                           b.description DESCRIPTION, 
                           a.REQUIRED_QUANTITY QUANTITY ,
                           a.SUPPLY_SUBINVENTORY SUBINVENTORY_CODE ,
                           DECODE(a.ORGANIZATION_ID,'1731','BXD','BXV') ORGANIZATION ,
                           a.OPERATION_SEQ_NUM OPERATION, 
                           ite.SEGMENT1   ASSEMBLY_PERE ,
                           loc.segment1 ||'.'|| loc.segment2 ||'.'|| loc.segment3 ||'.'|| loc.segment4 ||'.'|| loc.segment5 as LOCATOR

FROM    apps.WIP_ENTITIES         wdj, 
        apps.MTL_SYSTEM_ITEMS_B      ite ,
        apps.WIP_REQUIREMENT_OPERATIONS a,
        apps.MTL_SYSTEM_ITEMS_B      b,
        apps.MTL_ITEM_LOCATIONS       loc
        
WHERE  wdj.PRIMARY_ITEM_ID = ite.INVENTORY_ITEM_ID 
AND wdj.ORGANIZATION_ID = ite.ORGANIZATION_ID 
AND wdj.wip_entity_name like'18882043'
AND a.OPERATION_SEQ_NUM like '10'
and a.WIP_ENTITY_ID = wdj.WIP_ENTITY_ID

and a.OPERATION_SEQ_NUM not in (-10,-150)
and a.inventory_item_id = b.inventory_item_id
and a.organization_id = b.organization_id
and  a.supply_locator_id =loc.inventory_location_id (+)
AND ( wdj.CREATION_DATE > sysdate - 50)
                             
order by a.SUPPLY_SUBINVENTORY DESC, LOCATOR, ite.SEGMENT1 DESC
;