import { ProductService } from '../../services/ProductService';

describe('ProductService', () => {
  let productService: ProductService;

  beforeEach(() => {
    productService = new ProductService();
  });

  afterEach(async () => {
    await productService.disconnect();
  });

  describe('createProduct', () => {
    test('should create product with valid data', async () => {
      const productData = {
        sku: 'TEST001',
        name: 'Test Product',
        costPrice: 80,
        sellingPrice: 100,
        gstRate: 18,
        unit: 'PCS'
      };

      const userId = 'USER001';
      const companyId = 'COMP001';

      // This should not throw an error with valid data
      await expect(
        productService.createProduct(productData, userId, companyId)
      ).resolves.not.toThrow();
    });

    test('should reject invalid HSN code', async () => {
      const productData = {
        sku: 'TEST002',
        name: 'Test Product',
        costPrice: 80,
        sellingPrice: 100,
        gstRate: 18,
        hsnCode: '123', // Invalid - should be 2,4,6,8 digits
        unit: 'PCS'
      };

      const userId = 'USER001';
      const companyId = 'COMP001';

      await expect(
        productService.createProduct(productData, userId, companyId)
      ).rejects.toThrow('Invalid HSN code format');
    });

    test('should reject invalid GST rate', async () => {
      const productData = {
        sku: 'TEST003',
        name: 'Test Product',
        costPrice: 80,
        sellingPrice: 100,
        gstRate: 25, // Invalid rate
        unit: 'PCS'
      };

      const userId = 'USER001';
      const companyId = 'COMP001';

      await expect(
        productService.createProduct(productData, userId, companyId)
      ).rejects.toThrow('Invalid GST rate');
    });

    test('should reject duplicate SKU', async () => {
      const productData = {
        sku: 'TEST004',
        name: 'Test Product',
        costPrice: 80,
        sellingPrice: 100,
        gstRate: 18,
        unit: 'PCS'
      };

      const userId = 'USER001';
      const companyId = 'COMP001';

      // Create first product
      await productService.createProduct(productData, userId, companyId);

      // Try to create duplicate - should fail
      await expect(
        productService.createProduct(productData, userId, companyId)
      ).rejects.toThrow('already exists');
    });
  });

  describe('getProductById', () => {
    test('should return product details', async () => {
      const productId = 'PROD001';
      const companyId = 'COMP001';

      const product = await productService.getProductById(productId, companyId);
      
      expect(product).toBeDefined();
      expect(product.id).toBe(productId);
      expect(product.companyId).toBe(companyId);
    });

    test('should throw error for non-existent product', async () => {
      const productId = 'NONEXISTENT';
      const companyId = 'COMP001';

      await expect(
        productService.getProductById(productId, companyId)
      ).rejects.toThrow('Product not found');
    });
  });

  describe('updateProduct', () => {
    test('should update product with valid data', async () => {
      const productId = 'PROD001';
      const updateData = {
        name: 'Updated Product Name',
        sellingPrice: 150
      };

      const userId = 'USER001';
      const companyId = 'COMP001';

      const updatedProduct = await productService.updateProduct(productId, updateData, userId, companyId);
      
      expect(updatedProduct.name).toBe('Updated Product Name');
      expect(updatedProduct.sellingPrice).toBe(150);
    });

    test('should reject update with invalid pricing', async () => {
      const productId = 'PROD001';
      const updateData = {
        costPrice: 200, // Higher than selling price
        sellingPrice: 100
      };

      const userId = 'USER001';
      const companyId = 'COMP001';

      await expect(
        productService.updateProduct(productId, updateData, userId, companyId)
      ).rejects.toThrow('Cost price cannot be greater than selling price');
    });
  });

  describe('deleteProduct', () => {
    test('should soft delete product', async () => {
      const productId = 'PROD001';
      const userId = 'USER001';
      const companyId = 'COMP001';

      await expect(
        productService.deleteProduct(productId, userId, companyId)
      ).resolves.not.toThrow();

      // Verify product is inactive
      const product = await productService.getProductById(productId, companyId);
      expect(product.isActive).toBe(false);
    });

    test('should reject delete for product with stock', async () => {
      const productId = 'PROD_WITH_STOCK';
      const userId = 'USER001';
      const companyId = 'COMP001';

      await expect(
        productService.deleteProduct(productId, userId, companyId)
      ).rejects.toThrow('Cannot delete product with existing stock');
    });
  });

  describe('searchProducts', () => {
    test('should return products with pagination', async () => {
      const filters = {
        page: 1,
        limit: 10
      };

      const companyId = 'COMP001';

      const result = await productService.searchProducts(filters, companyId);
      
      expect(result).toHaveProperty('products');
      expect(result).toHaveProperty('total');
      expect(result).toHaveProperty('page');
      expect(result).toHaveProperty('limit');
      expect(Array.isArray(result.products)).toBe(true);
    });

    test('should filter products by category', async () => {
      const filters = {
        categoryId: 'CAT001',
        page: 1,
        limit: 10
      };

      const companyId = 'COMP001';

      const result = await productService.searchProducts(filters, companyId);
      
      // All returned products should belong to the specified category
      result.products.forEach(product => {
        expect(product.categoryId).toBe('CAT001');
      });
    });

    test('should search products by name', async () => {
      const filters = {
        search: 'Test',
        page: 1,
        limit: 10
      };

      const companyId = 'COMP001';

      const result = await productService.searchProducts(filters, companyId);
      
      // All returned products should contain 'Test' in name, SKU, or barcode
      result.products.forEach(product => {
        const searchableText = `${product.name} ${product.sku} ${product.barcode || ''}`.toLowerCase();
        expect(searchableText).toContain('test');
      });
    });
  });

  describe('searchByCode', () => {
    test('should find product by SKU', async () => {
      const code = 'TEST001';
      const companyId = 'COMP001';

      const product = await productService.searchByCode(code, companyId);
      
      expect(product).toBeDefined();
      expect(product.sku).toBe(code);
    });

    test('should find product by barcode', async () => {
      const code = 'BARCODE001';
      const companyId = 'COMP001';

      const product = await productService.searchByCode(code, companyId);
      
      expect(product).toBeDefined();
      expect(product.barcode).toBe(code);
    });

    test('should throw error for non-existent code', async () => {
      const code = 'NONEXISTENT';
      const companyId = 'COMP001';

      await expect(
        productService.searchByCode(code, companyId)
      ).rejects.toThrow('Product not found');
    });
  });
});