
'''
def manage_presave_product(original_product, changed_product, current_fmcg):
    if changed_product.fmcg_product.id == original_product.fmcg_product.id:    
        current_fmcg.quantity_in_stock = current_fmcg.quantity_in_stock + original_product.quantity_taken_from_fmcg_product - changed_product.quantity_taken_from_fmcg_product
        current_fmcg.save()
    else:
        old_fmcg = current_fmcg
        new_fmcg = changed_product.fmcg_product
        old_fmcg.quantity_in_stock = old_fmcg.quantity_in_stock + original_product.quantity_taken_from_fmcg_product
        new_fmcg.quantity_in_stock = new_fmcg.quantity_in_stock - changed_product.quantity_taken_from_fmcg_product
        old_fmcg.save()
        new_fmcg.save()
'''