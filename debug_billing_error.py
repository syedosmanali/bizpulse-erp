import sqlite3
import json
from datetime import datetime

print("=" * 60)
print("BILLING ERROR DEBUG - बिलिंग एरर डिबग")
print("=" * 60)

# Check database structure
conn = sqlite3.connect('billing.db')
cursor =  60)
 *"
print("=plete!")("Debug Comint* 60)
pr=" + "\n" "int(ose()

prconn.cl
ilable!")
th stock avaucts wiNo prod"   ❌   print(lse:
  })")
eock: {p[3]]} (St1]}: ₹{p[2f"   - {p[nt(      pris:
  uctin prod
    for p esting:")or ts fable productAvailprint("   
     products:tchall()
if cursor.fets =3")
produc 0 LIMIT  stock > WHEREductsROM proe, stock Ficd, name, pr ite("SELECTursor.execu
c")...stingts for teg producheckin5. Cnt("\n

prirint_exc()k.pacebac")
    trror:  Full er\n ("
    printracebackrt tpo ime}")
   ror: {(f"   ❌ Errinte:
    pas on t Excepti  
excep)")
   (not savedled backa rol dat("   ✅ Test   printollback()
     conn.rst data
te Rollback     #  
sful")
  cces sucord insert ✅ Sales rerint("  
    p   ))
    mp
      timesta),
   estamp.time(im t),
       mp.date(     timesta0,
   18.     100.0,
         100.0,
       1,
           oduct',
    'Test Pr
    -1',rod  'p     _number,
 ll        bil_id,
  bil      e_id,
sal         (
?)
    ''',, , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?ES (?    VALUd_at)
    eatee_time, cre, salsale_dat                        unt, 
 mo tax_aice,_pralce, totnit_pri, utity      quan           
         name, product_oduct_id,prll_number, l_id, bi bils (id,RT INTO sale      INSE'
  execute(''ursor.    cd4())
d.uui str(uui_id =   saled
 ecors rinsert saleo # Try t
    
    ccessful")nsert suem iBill it"   ✅ print(
    
    
    ))100.0      100.0,
  ,
                1',
ctrodu  'Test P1',
        'prod-,
      ll_idbi
           item_id,', (
      ?)
    '', ?, ?(?, ?, ?, ?,ALUES  V       rice)
otal_pe, t   unit_pric                 
          ntity,  quame,naroduct_uct_id, p, prod(id, bill_iditems bill_NSERT INTO '
        I(''teursor.execu)
    c4()uuiduid. = str(um_iditeem
     itert billTry to ins  #  
  ")
   essfult succ✅ Bill insert("     
    prin   ))
  timestamp
        mpleted',
        'co18.0,
       1,
      0.0
      18.0,     
      100.0,   etail',
     'rumber,
     bill_nd,
      l_i   bil     ''', (
, ?)
    , ?, ?, ?, ?, ?ES (?, ?, ?   VALU     at)
created_tus,  sta_amount,otalnt_amount, tou disc                      ount, 
  x_am tabtotal,s_type, sunesusil_number, bls (id, bilTO bilRT IN       INSE
 execute('''cursor.bill
    rt y to inse
    # Tr)
    }"umberill_nmber: {b   Bill Nu  print(f"")
  d}bill_i {   Bill ID:t(f"  prin'
    
  %H%M%S")}("%Y%m%dme.strftiT-{timestampTES f' = bill_number)
   atetime.now( = dtampimes t))
   uid4(id.u(uu str bill_id =ta
   t da
    # Tes uuid
       import)
try:
 ..."uallyation man creting bill"\n4. Tes
print()
nt"esens pred columirAll requnt(f"   ✅ rie:
    p")
elsles)}(missing_sa', '.joinlumns: {ssing co Mi   ❌ print(f"sales:
   issing_ls]
if ms_co in sales if col notcol_sales_red requior col ins = [col fsing_sale]
mis_at' 'createdime',ale_te_date', 's   'sal                   amount',
 x_price', 'tace', 'total_nit_printity', 'u 'qua                     me',
 duct_narod', 'product_ir', 'pll_numbeid', 'bill_ ['id', 'bis =_col_salesquired)

reols)}"join(sales_cs: {', '.f"   Columnt(in()]
prr.fetchallcurso col in 1] for = [col[les_colses)")
saalle_info(sAGMA tabcute("PRcursor.exe")
cture...ru stable SALES tChecking"\n3. int(t")

prlumns presenuired coll reqnt(f"   ✅ A
    pri
else:s)}")ing_itemiss(m: {', '.joinlumnsng cosif"   ❌ Mis
    print(ng_items:f missiols]
items_ct in inos if col ed_items_col in requirr colms = [col foing_ite
miss_price']ce', 'totalnit_pri         'u            , 
  ntity'me', 'qua 'product_nad',_id', 'product', 'bill_i= ['idls ed_items_co

requirls)}")in(items_cons: {', '.jolum"   Co
print(f()].fetchallursorin cr col ol[1] focols = [c")
items__items)billble_info(ta("PRAGMA or.execute")
cursre...tuuctable strEMS _ITecking BILL\n2. Ch
print("ent")
olumns presquired c ✅ All ret(f"   prin
   
else:ills)}")n(missing_bjoi{', '.g columns: issin❌ M   "t(fs:
    prinissing_billls]
if m_cobillsin  not  if colls_colsquired_bilor col in re= [col fs ng_bill
missieated_at'] 'crstatus',_amount', 'unt', 'totalscount_amo 'di                   
   x_amount', ', 'ta', 'subtotalusiness_type 'bber',um_n'billd', s_cols = ['ired_bill

requi")}_cols)oin(bills'.j,  {'umns: Col"  ()]
print(fllr.fetcha cursofor col inol[1]  [cs_cols =s)")
billle_info(bill"PRAGMA tabecute(
cursor.exture...")ble strucLLS tacking BIChe"\n1. ()

print(conn.cursor